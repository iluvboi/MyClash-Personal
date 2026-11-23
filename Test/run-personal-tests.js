'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('mihomoScript.js', 'utf8');

// Parse first: catches syntax errors before any runtime checks.
new vm.Script(source, { filename: 'mihomoScript.js' });

// Personal region and icon regression checks.
const regions = ['香港', '日本', '美国', '新加坡', '台湾', '韩国', '加拿大', '印度', '德国', '法国', '澳大利亚', '英国', 'VIP'];
for (const name of regions) assert(source.includes(`name: '${name}'`), `missing region: ${name}`);
assert(source.includes('common/AsiaMap.svg'), 'Taiwan icon customization missing');
assert(source.includes('common/VIP.svg'), 'VIP icon customization missing');
assert(source.includes("flag: '🏝️'"), 'Taiwan flag customization missing');
assert(source.includes('common/AsiaMap.svg'), 'Taiwan icon customization missing');
assert(!source.includes('activeRegionDefinitions'), 'upstream region-selection logic must remain unchanged');

assert(source.includes("AWAvenue-Ads-Rule-Clash-No.Unwelcome.mrs"), 'AWAvenue ads+privacy MRS source missing');
assert(source.includes("privacy-protection-tools/anti-ad.github.io/master/docs/mihomo.mrs"), 'anti-AD MRS source missing');
assert(source.includes("'RULE-SET,category-ads,AdBlock'"), 'original category-ads rule missing');
assert(source.includes("'RULE-SET,awa_ads,AdBlock'"), 'AWAvenue rule missing');
assert(source.includes("'RULE-SET,anti_ad,AdBlock'"), 'anti-AD rule missing');

// Execute the script in an isolated context and smoke-test main() with a minimal subscription.
const sandbox = { console };
vm.createContext(sandbox);
vm.runInContext(source, sandbox, { filename: 'mihomoScript.js' });
assert.equal(typeof sandbox.main, 'function', 'main() was not defined');
const output = sandbox.main({
  proxies: [
    { name: '🇭🇰 香港 01', type: 'ss', server: 'hk.example.com', port: 443, cipher: 'aes-256-gcm', password: 'test' },
    { name: '🇯🇵 日本 01', type: 'ss', server: 'jp.example.com', port: 443, cipher: 'aes-256-gcm', password: 'test' },
    { name: '🇺🇸 美国 01', type: 'ss', server: 'us.example.com', port: 443, cipher: 'aes-256-gcm', password: 'test' },
  ],
});
assert(Array.isArray(output.proxies) && output.proxies.length > 0, 'main() returned no proxies');
assert(Array.isArray(output['proxy-groups']) && output['proxy-groups'].length > 0, 'main() returned no proxy groups');
assert(Array.isArray(output.rules) && output.rules.length > 0, 'main() returned no rules');
assert(output.dns && typeof output.dns === 'object', 'main() returned no DNS configuration');


function adBlockSmokeTest(minimalMode) {
  const ctx = { console };
  vm.createContext(ctx);
  vm.runInContext(source, ctx, { filename: 'mihomoScript.js' });
  if (minimalMode) vm.runInContext('ruleOptionsEnable.极简国内外分流模式 = true;', ctx);
  const out = ctx.main({
    proxies: [
      { name: '🇭🇰 香港 01', type: 'ss', server: 'hk.example.com', port: 443, cipher: 'aes-256-gcm', password: 'test' },
      { name: '🇯🇵 日本 01', type: 'ss', server: 'jp.example.com', port: 443, cipher: 'aes-256-gcm', password: 'test' },
    ],
  });
  const group = out['proxy-groups'].find((g) => g.name === 'AdBlock');
  assert(group, `AdBlock policy group missing (minimalMode=${minimalMode})`);
  assert.deepEqual(Array.from(group.proxies), ['REJECT', 'REJECT-DROP', 'PASS']);
  for (const name of ['category-ads', 'awa_ads', 'anti_ad']) {
    assert(out['rule-providers'][name], `missing provider: ${name} (minimalMode=${minimalMode})`);
    assert(out.rules.includes(`RULE-SET,${name},AdBlock`), `missing rule: ${name} (minimalMode=${minimalMode})`);
  }
}
adBlockSmokeTest(false);
adBlockSmokeTest(true);

console.log('Personal checks passed: syntax, 13 regions, Taiwan customization, three AdBlock providers, normal/minimal mode runtime checks, and main() smoke test.');

