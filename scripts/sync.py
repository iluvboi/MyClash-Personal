#!/usr/bin/env python3
"""Generate the personal Mihomo script from the latest AIsouler/MyClash upstream."""
from __future__ import annotations

import re
import subprocess
import urllib.request
from pathlib import Path

UPSTREAM_RAW = "https://raw.githubusercontent.com/AIsouler/MyClash/main/Script/mihomoScript.js"
OUTPUT = Path("mihomoScript.js")
SHA_FILE = Path("upstream.sha")

# Only additions to upstream regionDefinitions, plus Taiwan's flag/icon.
ADDITIONAL_REGIONS = r"""
  {
    name: '韩国',
    flag: '🇰🇷',
    regex: /🇰🇷|(?<!北)(?:韩国|南韩)|首尔|汉城|仁川|春川|釜山|大邱|大田|光州|济州|(?<![A-Za-z])(?:KR|KOR|ICN|(?<!North\s*)(?<!NORTH\s*)(?:[Kk]orea|KOREA)(?:n|N)?|[Ss]eoul|SEOUL|[Ii]ncheon|INCHEON|[Cc]huncheon|CHUNCHEON|[Bb]usan|BUSAN|[Pp]usan|PUSAN|[Jj]eju|JEJU)(?![A-Za-z])/,
    icon: 'https://cdn.jsdelivr.net/gh/appshubcc/Qure_Style_SVG@main/icon/svg/flag/South_Korea.svg',
  },
  {
    name: '加拿大',
    flag: '🇨🇦',
    regex: /🇨🇦|加拿大|多伦多|温哥华|蒙特利尔|渥太华|卡尔加里|(?<![A-Za-z])(?:CA|CAN)(?![A-Za-z])|canada/i,
    icon: 'https://cdn.jsdelivr.net/gh/appshubcc/Qure_Style_SVG@main/icon/svg/flag/Canada.svg',
  },
  {
    name: '印度',
    flag: '🇮🇳',
    regex: /🇮🇳|印度|孟买|新德里|德里|班加罗尔|金奈|海得拉巴|(?<![A-Za-z])IND(?![A-Za-z])|india/i,
    icon: 'https://cdn.jsdelivr.net/gh/appshubcc/Qure_Style_SVG@main/icon/svg/flag/India.svg',
  },
  {
    name: '德国',
    flag: '🇩🇪',
    regex: /🇩🇪|德国|柏林|法兰克福|慕尼黑|汉堡|杜塞尔多夫|(?<![A-Za-z])(?:DE|DEU|GER)(?![A-Za-z])|germany/i,
    icon: 'https://cdn.jsdelivr.net/gh/appshubcc/Qure_Style_SVG@main/icon/svg/flag/Germany.svg',
  },
  {
    name: '法国',
    flag: '🇫🇷',
    regex: /🇫🇷|法国|巴黎|马赛|里昂|(?<![A-Za-z])(?:FR|FRA)(?![A-Za-z])|france/i,
    icon: 'https://cdn.jsdelivr.net/gh/appshubcc/Qure_Style_SVG@main/icon/svg/flag/France.svg',
  },
  {
    name: '澳大利亚',
    flag: '🇦🇺',
    regex: /🇦🇺|澳大利亚|澳洲|悉尼|墨尔本|布里斯班|珀斯|阿德莱德|(?<![A-Za-z])(?:AU|AUS)(?![A-Za-z])|australia/i,
    icon: 'https://cdn.jsdelivr.net/gh/appshubcc/Qure_Style_SVG@main/icon/svg/flag/Australia.svg',
  },
  {
    name: '英国',
    flag: '🇬🇧',
    regex: /🇬🇧|英国|伦敦|曼彻斯特|伯明翰|格拉斯哥|爱丁堡|(?<![A-Za-z])(?:UK|GB|GBR)(?![A-Za-z])|united\s*kingdom|great\s*britain|britain|england/i,
    icon: 'https://cdn.jsdelivr.net/gh/appshubcc/Qure_Style_SVG@main/icon/svg/flag/United_Kingdom.svg',
  },
  {
    name: 'VIP',
    regex: /(?<![A-Za-z])VIP(?![A-Za-z])/i,
    icon: 'https://cdn.jsdelivr.net/gh/appshubcc/Qure_Style_SVG@main/icon/svg/common/VIP.svg',
  },
"""
def get_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "MyClash-Personal-Sync"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8")

def patch_regions(source: str) -> str:
    pattern = re.compile(
        r"(// 定义地区策略组\s*\nconst\s+regionDefinitions\s*=\s*\[)(.*?)(\n\];)",
        re.S,
    )
    matches = list(pattern.finditer(source))
    if len(matches) != 1:
        raise RuntimeError(f"Expected one upstream regionDefinitions block, found {len(matches)}; refusing to publish.")
    block = matches[0].group(2)
    taiwan_pattern = re.compile(
        r"(\{\s*name:\s*'台湾',.*?flag:\s*)'🇹🇼'(,\s*regex:.*?icon:\s*)\`\$\{iconBaseUrl\}Taiwan\.svg\`(,\s*\})",
        re.S,
    )
    block, count = taiwan_pattern.subn(
        lambda m: m.group(1) + "'🏝️'" + m.group(2)
        + "'https://cdn.jsdelivr.net/gh/appshubcc/Qure_Style_SVG@main/icon/svg/common/AsiaMap.svg'"
        + m.group(3),
        block,
    )
    if count != 1:
        raise RuntimeError(f"Expected exactly one Taiwan flag/icon entry, found {count}; refusing to publish.")
    if "name: '韩国'" in block or "name: 'VIP'" in block:
        raise RuntimeError("Personal region additions already exist upstream; refusing duplicate insertion.")
    updated_block = block.rstrip() + "\n" + ADDITIONAL_REGIONS.rstrip()
    return source[:matches[0].start()] + matches[0].group(1) + updated_block + matches[0].group(3) + source[matches[0].end():]

def main() -> None:
    upstream = get_text(UPSTREAM_RAW)
    result = subprocess.run(
        ["git", "ls-remote", "https://github.com/AIsouler/MyClash.git", "refs/heads/main"],
        check=True, capture_output=True, text=True, timeout=60,
    )
    commit_sha = result.stdout.split()[0] if result.stdout.split() else None
    if not isinstance(commit_sha, str) or len(commit_sha) != 40:
        raise RuntimeError("Could not identify upstream main commit SHA via git ls-remote.")
    generated = patch_regions(upstream)
    OUTPUT.write_text(generated, encoding="utf-8")
    SHA_FILE.write_text(commit_sha + "\n", encoding="utf-8")
    print(f"Generated {OUTPUT} from AIsouler/MyClash commit {commit_sha}")

if __name__ == "__main__":
    main()
