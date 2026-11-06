# CPU Side Channel Atlas

中文学习网站：[https://shundazhang.github.io/side-channel-atlas/](https://shundazhang.github.io/side-channel-atlas/)

面向已有 x86 / Arm / RISC-V 基础的安全与系统工程师，串联 CPU 侧信道、瞬态执行、代表性真实漏洞、原作者研究 PoC 和分层防御。

## 内容

- `index.html`：8 阶段学习路径与概念地图
- `foundations.html`：乱序核心结构图、缓存地址映射、Flush+Reload 与 Prime+Probe 逐步图解、逐出集合、瞬态执行攻击链
- `measurement.html`：缓存计时校准、ROC、噪声与滤波、缓存模板、频域筛选、置信区间与泄漏检验
- `cases.html`：Spectre、Meltdown、Foreshadow、MDS、BHI、Downfall、Inception、Zenbleed
- `labs.html`：两个纯浏览器模型、本机自有缓冲区计时实验、原作者 PoC 入口
- `defense.html`：分层防御、只读系统状态检查、TEE / RISC-V 延伸与一手资料

网站为静态 HTML/CSS/JavaScript，不加载第三方脚本、不收集数据。`examples/cache_timing.c` 仅访问本进程自有缓冲区，不测试漏洞或读取他人数据。

原始研究 PoC 链接指向作者仓库或论文；PoC 的执行条件、准确性和许可证以原作者说明为准。缓存测量与机制导读更新于 2026-11-06。

在支持 CLFLUSH 和 RDTSCP 的原生 x86-64 主机上，可用 `./cache_timing --csv` 导出按采集顺序排列的热读／逐出计时对。计时单位为 TSC 刻度。
