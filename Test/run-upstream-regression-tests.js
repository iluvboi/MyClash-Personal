'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('mihomoScript.js', 'utf8');
new vm.Script(source, { filename: 'mihomoScript.js' });

function sandbox() {
  const context = { console };
  vm.createContext(context);
  vm.runInContext(source, context, { filename: 'mihomoScript.js' });
  return context;
}
function config(extra = {}) {
  return {
    proxies: [
      { name: '🇭🇰 香港 01', type: 'ss', server: 'hk.example.com', port: 443, cipher: 'aes-256-gcm', password: 'test' },
      { name: '🇯🇵 日本 01', type: 'ss', server: 'jp.example.com', port: 443, cipher: 'aes-256-gcm', password: 'test' },
      { name: '🇺🇸 美国 01', type: 'ss', server: 'us.example.com', port: 443, cipher: 'aes-256-gcm', password: 'test' },
      { name: '订阅已用流量 10GB', type: 'ss', server: 'info.example.com', port: 443, cipher: 'aes-256-gcm', password: 'test' },
    ],
    ...extra,
  };
}

// DNS: core resolver behavior and fake-IP filtering remain present.
{
  const out = sandbox().main(config());
  assert.equal(out.dns.enable, true);
  assert.equal(out.dns['enhanced-mode'], 'fake-ip');
  assert.equal(out.dns['use-hosts'], true);
  assert(Array.isArray(out.dns['fake-ip-filter']));
  assert(out.hosts['doh.pub']);
  assert(out.hosts['dns.google']);
}

// Hosts: with no proxy-server-nameserver, host overrides are applied to node server names.
{
  const out = sandbox().main(config({ hosts: { 'hk.example.com': '192.0.2.10' }, dns: {} }));
  const hk = out.proxies.find((p) => p.name.includes('香港'));
  assert(hk);
  assert.equal(hk.server, '192.0.2.10');
}

// Filtering: informational subscription entries are excluded, valid regional nodes survive.
{
  const out = sandbox().main(config());
  const names = out.proxies.map((p) => p.name);
  assert(names.some((n) => n.includes('香港')));
  assert(!names.some((n) => n.includes('已用流量')));
}

// Chain: a custom landing proxy must dial through the generated transit group.
{
  const ctx = sandbox();
  vm.runInContext(`
    ruleOptionsEnable.链式代理 = true;
    customizeProxies.push({
      name: '落地-日本', type: 'ss', server: 'landing.example.com',
      port: 443, cipher: 'aes-256-gcm', password: 'test'
    });
  `, ctx);
  const out = ctx.main(config());
  const landing = out.proxies.find((p) => p.name.includes('落地-日本'));
  assert(landing);
  assert.equal(landing['dialer-proxy'], '链式中转');
  assert(out['proxy-groups'].some((g) => g.name === '链式中转'));
  assert(out['proxy-groups'].some((g) => g.name === '链式落地'));
}
console.log('Upstream regression checks passed: DNS, hosts, node filtering, chain proxy.');
