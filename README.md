# 课程全局笔记

将2026年8月的118份课程资料，按两个课题重新组织成可追溯的图表笔记。

- 神经重置：8.15–8.16，45份材料，8个主题。
- 女性脑科学：8.27–8.29，73份材料，10个主题。
- 输出包含两课PDF、合订本、Markdown、CSV出处索引和可离线阅读的网站。

## 阅读

打开 `docs/index.html` 即可离线阅读。搜索和出处弹窗均在浏览器本地运行，不依赖服务器或第三方服务。手机窄屏下表格可在表格区域横向滑动。

完整资料位于网站的“下载资料”区域。正文没有附上逐字稿或旧版逐篇PDF。每个出处提供日期、源文件名、独立笔记第1页以及当日合订本的物理页序，供回查原资料。

课程模型、现场观察、整理补充和外部核对分开表达。课堂个案采用匿名主题描述，不包含可识别个人身份或私密经历细节。8.15的11号文件已纳入最新版。

## 项目结构

```text
docs/                 可直接部署的静态网站
  assets/             样式、交互及搜索/来源数据
  downloads/          PDF、文本与资料包
data/sources.json     118份资料的页码与校验值
tools/content.py      两门课的结构化正文（编辑入口）
tools/build.py        生成网站、Markdown和PDF
tools/make_pdf.py     PDF排版和可点击引用
tools/package.py      生成阅读包与源码包
tools/verify.py       校验原件哈希、来源页码、PDF链接和网站路径
tools/browser_qa.cjs  桌面、手机与离线交互检查
.github/workflows/    GitHub Pages发布配置
```

## 修改内容

在 `tools/content.py` 中编辑正文，再运行 `python tools/build.py`。PDF生成需要Python的reportlab和pypdf；字体使用Windows的微软雅黑。网页和文本生成可单独运行 `python tools/build.py --html-only`，该方式不依赖PDF库或Windows字体。

已提交的 `data/sources.json` 足以重建输出，不需要重新读取原文。只有更新原有逐篇资料时才运行 `--refresh-sources`；当前源目录配置为 `D:\gwl`。刷新后应重新核对页码和文件哈希。

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
