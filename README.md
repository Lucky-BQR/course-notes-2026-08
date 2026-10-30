# 课程全局笔记

将2026年8月的118份课程资料，按两个课题重新组织成可追溯的图表笔记。

[在线阅读](https://lucky-bqr.github.io/course-notes-2026-08/) · [完整资料包](https://lucky-bqr.github.io/course-notes-2026-08/downloads/course-notes-complete.zip) · [GitHub仓库](https://github.com/Lucky-BQR/course-notes-2026-08)

- 神经重置：8.15–8.16，45份材料，8个主题。
- 女性脑科学：8.27–8.29，73份材料，10个主题。
- 输出包含两课PDF、合订本、Markdown、CSV出处索引和可离线阅读的网站。

## 阅读

打开 `docs/index.html` 即可离线阅读。搜索和出处弹窗均在浏览器本地运行，不依赖服务器或第三方服务。手机窄屏下表格可在表格区域横向滑动。

新增“每日详解”：8.15共21篇、8.16共24篇、8.27共26篇、8.28共24篇、8.29共23篇，合计118篇。点击全局笔记中的出处编号，可以进入具体详解、打开对应PDF页，再返回原来的全局章节。每页右下角均有“回到顶部”，单击立即返回。

每日笔记PDF只收录已有结构化笔记页，不含逐字稿及源文件附件；页码按每日笔记版重新编号。出处弹窗同时保留原资料的文件名和物理页序，避免与新笔记版混淆。原有两课全局正文及三份PDF保持不变。

完整资料位于网站的“下载资料”区域。正文没有附上逐字稿或旧版逐篇PDF。每个出处提供日期、源文件名、独立笔记第1页以及当日合订本的物理页序，供回查原资料。

课程模型、现场观察、整理补充和外部核对分开表达。课堂个案采用匿名主题描述，不包含可识别个人身份或私密经历细节。8.15的11号文件已纳入最新版。

## 项目结构

```text
docs/                 可直接部署的静态网站
  assets/             样式、交互及搜索/来源数据
  downloads/          PDF、文本与资料包
data/sources.json     118份资料的页码与校验值
data/daily.json       五天118篇已整理笔记及各自参考资料
tools/content.py      两门课的结构化正文（编辑入口）
tools/build.py        生成网站、Markdown和PDF
tools/make_pdf.py     PDF排版和可点击引用
tools/daily.py        每日详解网页、索引、笔记版PDF与反向导航
tools/package.py      生成阅读包与源码包
tools/verify.py       校验原件哈希、来源页码、PDF链接和网站路径
tools/browser_qa.cjs  桌面、手机与离线交互检查
.github/workflows/    GitHub Pages发布配置
```

## 修改内容

在 `tools/content.py` 中编辑全局正文，在 `data/daily.json` 中维护每日笔记。运行 `python tools/build.py --html-only` 可生成网页与文本，不会重写PDF，也不依赖PDF库或Windows字体。

需要生成每日笔记PDF时，运行 `python tools/build.py --html-only --daily-pdfs`，它从原始逐篇PDF提取笔记页并重新编号，保留原件。完整PDF构建需要Python的reportlab和pypdf，字体使用Windows微软雅黑。运行不带参数的 `python tools/build.py` 会同时重建全局和每日PDF。

已提交的两份data JSON足以重建网页，不需要重新读取原文。只有更新原有逐篇资料时才运行 `--refresh-sources` 或 `--refresh-daily`；当前源目录配置为 `D:\gwl`。刷新后应重新核对页码和文件哈希。

最后运行 `python tools/package.py` 更新网站下载包。部署使用预先生成的静态文件，不在云端调用模型或生成PDF。

## GitHub部署

仓库采用 `docs/` 静态目录，所有链接均为相对路径，支持项目子路径。

1. 将项目上传至GitHub仓库。
2. 在仓库 `Settings → Pages → Source` 选择 `GitHub Actions`。
3. 向 `codex/course-notes` 分支推送，或手动运行“Publish course notes”。

工作流只发布 `docs/`，不会把本地源资料目录、验证截图或系统凭证上传为网站内容。

官方依据：[GitHub Pages发布源配置](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)、[自定义工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。

## Gitee

截至2026-10-30核对，Gitee帮助中心将Gitee Pages及Pages Pro标注为功能已下线。因此Gitee可用作代码/资料仓库镜像，本项目不提供已经失效的“一键Pages部署”步骤。在线阅读由GitHub Pages提供；如需国内托管，可把同一 `docs/` 目录部署到其他静态托管服务。

官方依据：[Gitee帮助中心](https://gitee.com/help.com/)。

## 核验口径

来源页码以当前独立PDF和当日合订本实际内容核对。源码中保留SHA256便于后续核查。没有统一可核验的录音时间戳，因此不编造分钟定位。QA结果与交付说明随最终资料包提供。
