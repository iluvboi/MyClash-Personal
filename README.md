# MyClash-Personal

个人定制的 MyClash Mihomo 脚本，基于 AIsouler/MyClash 上游自动同步。

## FlClash 托管脚本地址

`https://raw.githubusercontent.com/iluvboi/MyClash-Personal/main/mihomoScript.js`

将上面的 Raw 地址填入 FlClash 的 Mihomo 脚本/托管脚本 URL。

## 自动同步

- GitHub Actions 每天自动检查上游更新，也支持手动运行。
- 上游结构或脚本语法检查失败时，不会覆盖上一次可用脚本。
- 自定义地区：香港、日本、美国、新加坡、台湾（🏝️）、韩国、加拿大、印度、德国、法国、澳大利亚、英国、VIP。
- 自定义开关在 `scripts/sync.py` 中维护；生成文件为 `mihomoScript.js`。

上游： https://github.com/AIsouler/MyClash
