# CPU Side Channel Atlas

中文学习网站：[https://shundazhang.github.io/side-channel-atlas/](https://shundazhang.github.io/side-channel-atlas/)

面向已有 x86 / Arm / RISC-V 基础的安全与系统工程师，串联 CPU 侧信道、瞬态执行、代表性真实漏洞、原作者研究 PoC 和分层防御。

## 内容

- `index.html`：8 阶段学习路径与概念地图
- `foundations.html`：架构 / 微架构状态、缓存计时、Flush+Reload、Prime+Probe、瞬态执行攻击链
- `cases.html`：Spectre、Meltdown、Foreshadow、MDS、BHI、Downfall、Inception、Zenbleed
- `labs.html`：两个纯浏览器模型、本机自有缓冲区计时实验、原作者 PoC 入口
- `defense.html`：分层防御、只读系统状态检查、TEE / RISC-V 延伸与一手资料

网站为静态 HTML/CSS/JavaScript，不加载第三方脚本、不收集数据。`examples/cache_timing.c` 仅访问本进程自有缓冲区，不测试漏洞或读取他人数据。

原始研究 PoC 链接指向作者仓库或论文；PoC 的执行条件、准确性和许可证以原作者说明为准。网站内容核对于 2026-09-25。
