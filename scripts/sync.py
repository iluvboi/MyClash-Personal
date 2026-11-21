#!/usr/bin/env python3
"""Generate the personal Mihomo script from the latest AIsouler/MyClash upstream."""
from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

UPSTREAM_RAW = "https://raw.githubusercontent.com/AIsouler/MyClash/main/Script/mihomoScript.js"
UPSTREAM_COMMIT_API = "https://api.github.com/repos/AIsouler/MyClash/commits/main"
OUTPUT = Path("mihomoScript.js")
SHA_FILE = Path("upstream.sha")

REGION_BLOCK = r"""
// Personal region definitions maintained by MyClash-Personal.
const regionDefinitions = [
  {
    name: '香港',
    flag: '🇭🇰',
    regex: /🇭🇰|香港|(?<![A-Za-z])HKG?(?![A-Za-z])|hong\s*kong/i,
    icon: 'https://cdn.jsdelivr.net/gh/appshubcc/Qure_Style_SVG@main/icon/svg/flag/Hong_Kong.svg',
    default: true,
  },
  {
    name: '日本',
    flag: '🇯🇵',
    regex: /🇯🇵|日本|东京|大阪|京都|(?<![A-Za-z])JPN?(?![A-Za-z])|japan/i,
    icon: 'https://cdn.jsdelivr.net/gh/appshubcc/Qure_Style_SVG@main/icon/svg/flag/Japan.svg',
    default: true,
  },
  {
    name: '美国',
    flag: '🇺🇸',
    regex: /🇺🇸|美国|纽约|洛杉矶|旧金山|芝加哥|休斯顿|迈阿密|西雅图|波士顿|华盛顿|拉斯维加斯|圣何塞|(?<![A-Za-z])USA?(?![A-Za-z])|america|united\s*states/i,
    icon: 'https://cdn.jsdelivr.net/gh/appshubcc/Qure_Style_SVG@main/icon/svg/flag/United_States.svg',
    default: true,
  },
  {
    name: '新加坡',
    flag: '🇸🇬',
    regex: /🇸🇬|新加坡|狮城|(?<![A-Za-z])SGP?(?![A-Za-z])|singapore/i,
    icon: 'https://cdn.jsdelivr.net/gh/appshubcc/Qure_Style_SVG@main/icon/svg/flag/Singapore.svg',
    default: true,
  },
  {
    name: '台湾',
    flag: '🏝️',
    regex: /🏝️|台湾|台北|高雄|(?<![A-Za-z])TWN?(?![A-Za-z])|taiwan/i,
    icon: 'https://cdn.jsdelivr.net/gh/appshubcc/Qure_Style_SVG@main/icon/svg/common/AsiaMap.svg',
    default: true,
  },
  {
    name: '韩国',
    flag: '🇰🇷',
    regex: /🇰🇷|(?<!北)(?:韩国|南韩)|首尔|汉城|仁川|春川|釜山|大邱|大田|光州|济州|(?<![A-Za-z])(?:KR|KOR|ICN|(?<!North\s*)(?<!NORTH\s*)(?:[Kk]orea|KOREA)(?:n|N)?|[Ss]eoul|SEOUL|[Ii]ncheon|INCHEON|[Cc]huncheon|CHUNCHEON|[Bb]usan|BUSAN|[Pp]usan|PUSAN|[Jj]eju|JEJU)(?![A-Za-z])/,
    icon: 'https://cdn.jsdelivr.net/gh/appshubcc/Qure_Style_SVG@main/icon/svg/flag/South_Korea.svg',
    default: true,
  },
  {
    name: '加拿大',
    flag: '🇨🇦',
    regex: /🇨🇦|加拿大|多伦多|温哥华|蒙特利尔|渥太华|卡尔加里|(?<![A-Za-z])(?:CA|CAN)(?![A-Za-z])|canada/i,
    icon: 'https://cdn.jsdelivr.net/gh/appshubcc/Qure_Style_SVG@main/icon/svg/flag/Canada.svg',
    default: true,
  },
  {
    name: '印度',
    flag: '🇮🇳',
    regex: /🇮🇳|印度|孟买|新德里|德里|班加罗尔|金奈|海得拉巴|(?<![A-Za-z])IND(?![A-Za-z])|india/i,
    icon: 'https://cdn.jsdelivr.net/gh/appshubcc/Qure_Style_SVG@main/icon/svg/flag/India.svg',
    default: true,
  },
  {
    name: '德国',
    flag: '🇩🇪',
    regex: /🇩🇪|德国|柏林|法兰克福|慕尼黑|汉堡|杜塞尔多夫|(?<![A-Za-z])(?:DE|DEU|GER)(?![A-Za-z])|germany/i,
    icon: 'https://cdn.jsdelivr.net/gh/appshubcc/Qure_Style_SVG@main/icon/svg/flag/Germany.svg',
    default: true,
  },
  {
    name: '法国',
    flag: '🇫🇷',
    regex: /🇫🇷|法国|巴黎|马赛|里昂|(?<![A-Za-z])(?:FR|FRA)(?![A-Za-z])|france/i,
    icon: 'https://cdn.jsdelivr.net/gh/appshubcc/Qure_Style_SVG@main/icon/svg/flag/France.svg',
    default: true,
  },
  {
    name: '澳大利亚',
    flag: '🇦🇺',
    regex: /🇦🇺|澳大利亚|澳洲|悉尼|墨尔本|布里斯班|珀斯|阿德莱德|(?<![A-Za-z])(?:AU|AUS)(?![A-Za-z])|australia/i,
    icon: 'https://cdn.jsdelivr.net/gh/appshubcc/Qure_Style_SVG@main/icon/svg/flag/Australia.svg',
    default: true,
  },
  {
    name: '英国',
    flag: '🇬🇧',
    regex: /🇬🇧|英国|伦敦|曼彻斯特|伯明翰|格拉斯哥|爱丁堡|(?<![A-Za-z])(?:UK|GB|GBR)(?![A-Za-z])|united\s*kingdom|great\s*britain|britain|england/i,
    icon: 'https://cdn.jsdelivr.net/gh/appshubcc/Qure_Style_SVG@main/icon/svg/flag/United_Kingdom.svg',
    default: true,
  },
  {
    name: 'VIP',
    regex: /(?<![A-Za-z])VIP(?![A-Za-z])/i,
    icon: 'https://cdn.jsdelivr.net/gh/appshubcc/Qure_Style_SVG@main/icon/svg/common/Airport.svg',
    default: true,
  },
];

// Respect the region checklist injected by Bettbox.
const enabledRegionNames =
  typeof bettboxRegions !== 'undefined' && Array.isArray(bettboxRegions)
    ? new Set(bettboxRegions)
    : null;
const activeRegionDefinitions = regionDefinitions.filter((region) =>
  enabledRegionNames ? enabledRegionNames.has(region.name) : region.default,
);
"""

# These are the user's saved settings mapped to names used by current upstream.
OVERRIDES = {
    "手动选择": True,
    "自动选择": False,
    "负载均衡": False,
    "AI": True,
    "FCM": True,
    "YouTube": True,
    "Google": True,
    "GitHub": True,
    "Microsoft": True,
    "Apple": True,
    "Telegram": True,
    "Steam": True,
    "TikTok": True,
    "Twitter": True,
    "Meta": True,
    "Netflix": True,
    "PikPak": False,
    "Spotify": False,
    "Crypto": True,
    "AdBlock": True,
    "极简国内外分流模式": False,
    "生成地区自动选择组": False,
    "隐藏地区手动选择组": False,
    "生成高低倍率组": False,
    "生成家宽节点组": False,
    "分流组添加所有节点": False,
    "过滤低倍率节点": False,
    "过滤高倍率节点": False,
    "过滤非地区节点": True,
    "屏蔽代理QUIC流量": True,
    "代理IPV4优先": False,
    "代理IPV6优先": False,
    "链式代理": False,
    "优先国内DNS加速": True,
}

def get_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "MyClash-Personal-Sync"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8")

def patch_options(source: str) -> str:
    match = re.search(r"const\s+ruleOptionsEnable\s*=\s*\{.*?\n\};", source, re.S)
    if not match:
        raise RuntimeError("Upstream ruleOptionsEnable block not found; refusing to publish.")
    block = match.group(0)
    for key, value in OVERRIDES.items():
        pattern = re.compile(r"(?m)^([ \t]*(?:['\"]?" + re.escape(key) + r"['\"]?)[ \t]*:[ \t]*)(true|false)([ \t]*,?)([ \t]*(?://.*)?)$")
        updated, count = pattern.subn(lambda m: m.group(1) + str(value).lower() + m.group(3) + (m.group(4) or ""), block)
        if count == 0 and key == "优先国内DNS加速":
            block = block.replace("\n};", "\n  优先国内DNS加速: true,\n};")
        elif count != 1:
            raise RuntimeError(f"Expected exactly one option '{key}', found {count}; refusing to publish.")
        else:
            block = updated
    return source[:match.start()] + block + source[match.end():]

def patch_regions(source: str) -> str:
    pattern = re.compile(r"//\s*定义地区策略组\s*\nconst\s+regionDefinitions\s*=\s*\[.*?\n\];(?=\s*\n//\s*定义倍率策略组)", re.S)
    matches = list(pattern.finditer(source))
    if len(matches) != 1:
        raise RuntimeError(f"Expected one upstream regionDefinitions block, found {len(matches)}; refusing to publish.")
    return source[:matches[0].start()] + REGION_BLOCK.strip() + source[matches[0].end():]

def main() -> None:
    upstream = get_text(UPSTREAM_RAW)
    commit_data = json.loads(get_text(UPSTREAM_COMMIT_API))
    commit_sha = commit_data.get("sha")
    if not isinstance(commit_sha, str) or len(commit_sha) < 40:
        raise RuntimeError("Could not identify upstream commit SHA.")
    generated = patch_regions(patch_options(upstream))

    # Bettbox reads this top-level declaration to render its region checklist.
    region_header = 'const bettboxRegions = ["香港","日本","美国","新加坡","台湾","韩国","加拿大","印度","德国","法国","澳大利亚","英国","VIP"];' + chr(10)
    if "const bettboxRegions" not in generated:
        generated = region_header + generated

    # Apply the selected regions consistently to strategy groups and proxy matching.
    generated = generated.replace(
        "const allRegionDefinitions = [...regionDefinitions, ...rateRegionDefinitions, ...homeRegionDefinitions];",
        "const allRegionDefinitions = [...activeRegionDefinitions, ...rateRegionDefinitions, ...homeRegionDefinitions];",
    )
    generated = generated.replace("regionDefinitions.includes(region)", "activeRegionDefinitions.includes(region)")
    required = ["const bettboxRegions = [", "const regionDefinitions = [", "default: true", "const activeRegionDefinitions = regionDefinitions.filter", "const allRegionDefinitions = [...activeRegionDefinitions", "activeRegionDefinitions.includes(region)", "common/AsiaMap.svg", "name: 'VIP'", "优先国内DNS加速: true"]
    for item in required:
        if item not in generated:
            raise RuntimeError(f"Generated script is missing required customization: {item}")
    OUTPUT.write_text(generated, encoding="utf-8")
    SHA_FILE.write_text(commit_sha + "\n", encoding="utf-8")
    print(f"Generated {OUTPUT} from AIsouler/MyClash commit {commit_sha}")

if __name__ == "__main__":
    main()
