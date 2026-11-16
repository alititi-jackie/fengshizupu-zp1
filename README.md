# zp1.fengshizupu.com — 各地冯氏旧谱收藏（第一站）

收录各地图书馆藏本冯氏宗谱影印（公有领域），逐页在线连读。入口在主站
fengshizupu.com「各地族谱」页（恩平谱、小湴村之后）。

## 架构
- 静态站，GitHub Pages + GitHub Actions 部署，自定义域名 zp1.fengshizupu.com（site/CNAME 由生成器输出）。
- 书目数据：`data/books.json`（书名、地区、年代、纂辑者、来源、各册页数与公有领域源文件 URL）。
- 构建流程（Actions）：从本站 Release `b-20261116` 下载源 PDF → `scripts/render_pages.py` 拆页、压页眉、转 WebP → `scripts/generate.py` 生成页面 → 部署。新书入库时把 PDF 加入该 Release（books.json 的 url 字段只作来源记录）。
- 每册源 PDF 约 30MB，不入库；本地备份在维护机 ~/workspace/fengshizupu-work/。
- 本站容量约 900MB 封顶，装满后开 zp2（新仓库+子域名，同一套代码）。

## 样式（与主站/恩平站统一）
- `assets/genealogy-theme.css` 是共享主题副本。**源头在主站仓库
  fengshizupu-site 的 `public/assets/genealogy-theme.css`**：改外观先改主站，
  再同步本站与恩平站（enpingfengshi-site 的 `assets/genealogy-theme.css`）。
- `assets/style.css`、`assets/site.js`、`assets/reader-controls.js` 沿用恩平站
  现行版本；阅读器为恩平连看阅读器（`assets/volume-reader.js` 按册适配：
  图片路径 /img/<slug>/<册id>/pNNNN.webp，页签「第 X 页」，无支系数据）。
- 页头/横向导航/页脚与主站相同；导航四项（首页/资讯/族谱/关于）链回主站
  绝对地址、本窗口打开，「族谱」高亮。

## 内容规则
- 只收公有领域馆藏影印，逐部注明藏本来源与纂修年代。
- 原书藏本馆水印保留不去除；每页左上方压「冯氏族谱 · fengshizupu.com」
  深红页眉（深色页自动用米白色），由 render_pages.py 完成。
- 加新书：books.json 加一条 → 推仓 → Actions 自动出页面；主站「各地族谱」
  页的入口由维护方另行添加。
