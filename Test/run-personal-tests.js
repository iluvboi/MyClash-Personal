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
assert(source.includes('const activeRegionDefinitions = regionDefinitions.filter'), 'Bettbox region selection filter missing');
assert(source.includes('[...activeRegionDefinitions, ...rateRegionDefinitions, ...homeRegionDefinitions]'), 'active regions are not used to build groups');
assert(source.includes('activeRegionDefinitions.includes(region)'), 'active regions are not used by node filtering');

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

console.log('Personal script checks passed: syntax, 13 regions, custom icons, Bettbox region filtering, and main() smoke test.');
