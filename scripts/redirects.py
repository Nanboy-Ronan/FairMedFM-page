"""Build the old site as redirects to https://fairmedfm.github.io/FairMedFM/, where FairMedFM is now published.

Every page that existed here becomes a page with a canonical link, an immediate meta refresh and a script that
keeps the #fragment; text files say where they moved; 404.html redirects any other path. The sitemap keeps the
old URLs so that search engines revisit them and follow the redirects.
"""
import datetime
import html
import json
import sys
from pathlib import Path

OLD = "https://nanboy-ronan.github.io/FairMedFM-page/"
NEW = "https://fairmedfm.github.io/FairMedFM/"
DOC_PAGES = ["", "installation/", "evaluate-your-model/", "how-to/", "metrics/", "cli/", "api/", "comparison/",
             "benchmark/", "models/", "datasets/", "reproduce/", "faq/", "citation/"]
TEXT_FILES = ["llms.txt", "llms-full.txt", "docs/llms.txt", "docs/llms-full.txt", "robots.txt"]


def redirect_page(target):
    url = html.escape(target, quote=True)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>FairMedFM has moved</title>
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url={url}">
<script>location.replace({json.dumps(target)} + location.hash);</script>
</head>
<body><p>FairMedFM has moved to <a href="{url}">{url}</a>.</p></body>
</html>
"""


def main(output):
    output = Path(output)
    paths = [""] + [f"docs/{page}" for page in DOC_PAGES]
    for path in paths:
        (output / path).mkdir(parents=True, exist_ok=True)
        (output / path / "index.html").write_text(redirect_page(NEW + path))
        if path.startswith("docs/"):
            (output / path / "index.md").write_text(f"This page has moved to {NEW}{path}index.md\n")
    for name in TEXT_FILES:
        (output / name).write_text(f"FairMedFM has moved to {NEW}. This file is now at {NEW}{name}\n")
    # Any other old path: the same path under the new site.
    (output / "404.html").write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>FairMedFM has moved</title>
<script>location.replace({json.dumps(NEW)} + location.pathname.replace(/^\\/FairMedFM-page\\/?/, "")
  + location.search + location.hash);</script>
</head><body><p>FairMedFM has moved to <a href="{NEW}">{NEW}</a>.</p></body></html>
""")
    today = datetime.date.today().isoformat()
    urls = "".join(f"<url><loc>{OLD}{path}</loc><lastmod>{today}</lastmod></url>" for path in paths)
    (output / "sitemap.xml").write_text('<?xml version="1.0" encoding="utf-8"?>\n'
                                        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    # The IndexNow key stays published so that the redirects can be submitted.
    for key in Path(__file__).resolve().parents[1].joinpath("verification").glob("*.txt"):
        (output / key.name).write_text(key.read_text())
    (output / ".nojekyll").touch()
    for path in paths:
        print(OLD + path)


if __name__ == "__main__":
    main(sys.argv[1])
