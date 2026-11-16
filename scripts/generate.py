#!/usr/bin/env python3
"""Generate the zp1 static site (各地冯氏旧谱收藏) into ./site.

Chrome (header/nav/footer) mirrors fengshizupu.com; styles come from the
shared assets/genealogy-theme.css (source of truth: main site repo
public/assets/genealogy-theme.css) plus assets/style.css carried over from
the Enping site. The reader reuses the Enping continuous-scroll reader
(reader-controls.js + volume-reader.js).
"""
import json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site")
DOMAIN = "https://zp1.fengshizupu.com"
MAIN = "https://fengshizupu.com"
THEME_V = "08b0b6543950"

FAB_SCRIPT = """
<script>
var ft = document.getElementById('fabTop');
function fabShow(){ ft.classList.toggle('on', window.scrollY > 900); }
window.addEventListener('scroll', fabShow, {passive: true}); fabShow();
ft.onclick = function(){ window.scrollTo({top: 0, behavior: 'smooth'}); };
function sharePage(){ var u = location.href, t = document.title;
  var description = document.querySelector('meta[name="description"]').content;
  if (navigator.share) { navigator.share({title: t, text: description, url: u}).catch(function(){}); }
  else if (navigator.clipboard) { navigator.clipboard.writeText(u).then(function(){ alert('链接已复制'); }); } }
</script>"""

FAB = """<div class="fab"><button id="fabTop" type="button" title="回到顶部" aria-label="回到顶部">↑</button><button id="fabBack" type="button" title="返回" aria-label="返回" onclick="history.back()">←</button></div>"""


def head(title, desc):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="stylesheet" href="/assets/style.css?v=shared-theme-1">
<link rel="stylesheet" href="/assets/genealogy-theme.css?v={THEME_V}">
</head>
<body class="site-theme">
"""


def header():
    return f"""<header class="site-header"><a class="brand" href="/"><img src="/icon.svg" alt="" width="46" height="46"><span>冯氏族谱<small>zp1.fengshizupu.com</small></span></a></header>
<nav class="mainnav" aria-label="主导航"><div class="mainnav-in"><a href="{MAIN}/">首页</a><a href="{MAIN}/news/">资讯</a><a href="{MAIN}/archives/" class="on" aria-current="page">族谱</a><a href="{MAIN}/about/">关于</a><span class="share-wrap"><button type="button" class="share-text" onclick="sharePage()">分享</button></span></div></nav>
"""


def footer():
    return f"""<footer class="site-footer">冯氏族谱 · 留存原谱，连接宗亲<br>
全国数字族谱平台 · <a href="{MAIN}/">fengshizupu.com</a> · <a href="{MAIN}/about/">关于本站</a></footer>
</body>
</html>
"""


def book_total_pages(book):
    return sum(v["pages"] for v in book["volumes"])


def index_page(books):
    by_prov = {}
    for b in books:
        by_prov.setdefault(b["province"], []).append(b)
    sections = ""
    for prov, items in by_prov.items():
        rows = ""
        for b in items:
            meta = f'{b["era"]} · {len(b["volumes"])} 册 · {book_total_pages(b)} 页'
            q = f'{b["title"]} {b["keywords"]}'
            rows += f'<a href="/book/{b["slug"]}.html" data-q="{q}"><span>{b["title"]}</span><span class="pg">{meta}</span></a>\n'
        sections += f'<section class="block"><h2>{prov}</h2>\n<div class="list">\n{rows}</div></section>\n'
    total_books = len(books)
    total_pages = sum(book_total_pages(b) for b in books)
    return head("各地冯氏旧谱收藏 · 冯氏族谱",
                "各地冯氏旧谱收藏：收录图书馆藏本冯氏宗谱影印，逐页在线连读。") + header() + f"""<main>
<section class="hero"><p class="eyebrow">全国冯氏宗亲 · 数字族谱档案</p>
<h1>各地冯氏旧谱收藏</h1>
<p>收录各地图书馆藏本冯氏宗谱影印（公有领域），逐页在线连读。目前收录 {total_books} 部、{total_pages} 页，陆续增补。</p>
<div class="searchbox"><input id="bookSearch" type="text" placeholder="输入地名或书名，如：乐清、湘潭、宗谱" aria-label="搜索收藏的族谱"><button type="button" onclick="document.getElementById('bookSearch').focus()">搜索</button></div>
<p class="note" id="bookStatus"></p>
</section>
{sections}<section class="block"><h2>收藏说明</h2>
<p class="note">本站只收录公有领域的图书馆藏本影印，每部均注明藏本来源与纂修年代；原书上的藏本馆水印予以保留，每页左上方加「冯氏族谱 · fengshizupu.com」页眉。族谱按省份列于本页，点开任意一部即可逐册连读。</p>
</section>
</main>
{FAB}
<script src="/assets/site.js?v=2"></script>
<script>filterList('bookSearch', 'bookStatus', '.list a', '部');</script>
""" + FAB_SCRIPT + footer()


def book_page(b):
    rows = ""
    for v in b["volumes"]:
        rows += (f'<a href="/read/{b["slug"]}-{v["id"]}.html"><span>{v["name"]}</span>'
                 f'<span class="pg">{v["pages"]} 页 · 打开阅读 ›</span></a>\n')
    desc = f'{b["title"]}：{b["era"]}，{b["editors"]}。{b["source"]}，全 {len(b["volumes"])} 册 {book_total_pages(b)} 页，在线连读。'
    return head(f'{b["title"]} · 冯氏族谱', desc) + header() + f"""<main>
<p class="crumb"><a href="/">旧谱收藏</a> / {b["province"]} · {b["place"]}</p>
<h1>{b["title"]}</h1>
<div class="kv">
<p><strong>纂修年代：</strong>{b["era"]}</p>
<p><strong>纂辑者：</strong>{b["editors"]}</p>
<p><strong>藏本来源：</strong>{b["source"]}</p>
<p><strong>全书规模：</strong>{len(b["volumes"])} 册，共 {book_total_pages(b)} 页</p>
</div>
<p>{b["intro"]}</p>
<section class="block"><h2>各册阅读</h2>
<div class="list">
{rows}</div></section>
<p class="note">阅读说明：点开任意一册即从第一页连续向下阅读，可跳页、可点图放大；原书水印为藏本馆印记，予以保留。</p>
</main>
{FAB}
""" + FAB_SCRIPT + footer()


def reader_page(b, v):
    title = f'{b["title"]}（{v["name"]}）'
    pages = [None] + [{"label": f"第 {i} 页"} for i in range(1, v["pages"] + 1)]
    numeric = {str(i): i for i in range(1, v["pages"] + 1)}
    data = {"title": title, "base": f'/img/{b["slug"]}/{v["id"]}/',
            "pages": pages, "numeric": numeric, "start": 1}
    data_json = json.dumps(data, ensure_ascii=False)
    return head(f'{title} · 在线连读 · 冯氏族谱',
                f'{title}在线连读：{b["era"]}，{b["source"]}。') + header() + f"""<div class="wrap">
<div class="readerbar">
<a class="nav" href="/book/{b["slug"]}.html">返回目录</a>
<span class="info" id="info" aria-live="polite"></span>
<span class="info" id="branchInfo"></span>
<span class="reader-spacer"></span>
<span class="modes"><button id="mSingle" type="button">单页</button><button id="mScroll" type="button">连看</button></span>
<button id="jumpToggle" type="button">跳页</button>
<label class="info jumpctl">页码 <input id="jump" type="number" min="1" max="{v['pages']}"></label>
<button class="primary" id="jumpBtn">跳页</button>
</div>
<div class="readerwrap">
<button id="singlePage" class="reader-image" type="button" aria-label="放大当前谱页"><img class="pageimg" id="pg" alt="族谱原书页"></button>
<div id="scrollView" style="display:none"></div>
<div class="pagenav"><a id="prev" href="#">← 上一页</a><a id="next" href="#">下一页 →</a></div>
</div>
</div>
<dialog id="imageDialog" class="image-dialog" aria-labelledby="imageLabel">
<div class="image-toolbar"><span id="imageLabel"></span><button type="button" id="imageZoom">放大查看</button><button type="button" id="imageClose">关闭</button></div>
<div class="image-viewport"><img id="imageLarge" alt=""></div>
</dialog>
{FAB}
<script src="/assets/site.js?v=2"></script>
<script id="originalReaderData" type="application/json">{data_json}</script>
<script src="/assets/reader-controls.js?v=1" defer></script>
<script src="/assets/volume-reader.js?v=1" defer></script>
""" + FAB_SCRIPT + footer()


def main():
    data = json.load(open(os.path.join(ROOT, "data", "books.json"), encoding="utf-8"))
    books = data["books"]
    if os.path.exists(OUT):
        # keep rendered images if present (img/ is produced by render_pages.py)
        img_dir = os.path.join(OUT, "img")
        saved = None
        if os.path.exists(img_dir):
            saved = os.path.join(ROOT, ".img-keep")
            if os.path.exists(saved):
                shutil.rmtree(saved)
            shutil.move(img_dir, saved)
        shutil.rmtree(OUT)
        os.makedirs(OUT)
        if saved:
            shutil.move(saved, img_dir)
    else:
        os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(OUT, "assets"))
    icon = open(os.path.join(ROOT, "assets", "icon.svg"), encoding="utf-8").read()
    for name in ("icon.svg", "favicon.svg"):
        open(os.path.join(OUT, name), "w", encoding="utf-8").write(icon)
    open(os.path.join(OUT, "CNAME"), "w").write("zp1.fengshizupu.com\n")

    urls = [f"{DOMAIN}/"]
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(index_page(books))
    os.makedirs(os.path.join(OUT, "book"))
    os.makedirs(os.path.join(OUT, "read"))
    for b in books:
        open(os.path.join(OUT, "book", b["slug"] + ".html"), "w", encoding="utf-8").write(book_page(b))
        urls.append(f'{DOMAIN}/book/{b["slug"]}.html')
        for v in b["volumes"]:
            name = f'{b["slug"]}-{v["id"]}.html'
            open(os.path.join(OUT, "read", name), "w", encoding="utf-8").write(reader_page(b, v))
            urls.append(f"{DOMAIN}/read/{name}")
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"<url><loc>{u}</loc></url>" for u in urls]
    sm.append("</urlset>")
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(sm))
    open(os.path.join(OUT, "robots.txt"), "w").write(
        f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n")
    print(f"generated {len(urls)} pages into site/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
