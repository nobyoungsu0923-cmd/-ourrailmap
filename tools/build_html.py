# -*- coding: utf-8 -*-
"""src/app.html + data/*.json → index.html (한 파일, 오프라인 동작)
사용법: python3 tools/build_html.py"""
import os
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rd = lambda *p: open(os.path.join(root, *p), encoding="utf-8").read()
html = rd("src", "app.html")
html = html.replace("/*__NETWORK__*/", rd("data", "network.json").strip())
html = html.replace("/*__KOREA__*/", rd("data", "korea.json").strip())
html = html.replace("/*__RIVERS__*/", rd("data", "rivers.json").strip())
open(os.path.join(root, "index.html"), "w", encoding="utf-8").write(html)
print("index.html", len(html.encode()) // 1024, "KB")
