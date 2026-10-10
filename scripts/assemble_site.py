"""Combine the project page with the built documentation in the Pages artifact.

Usage: assemble_site.py SITE_DIR DOCS_CHECKOUT, where DOCS_CHECKOUT is a full clone of FairMedFM/FairMedFM.
Prints the URLs changed since yesterday, for IndexNow.
"""
import datetime
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SITE = "https://nanboy-ronan.github.io/FairMedFM-page/"
DOCS = SITE + "docs/"
ROOT = Path(__file__).resolve().parents[1]
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


def last_commit_date(repo, *paths):
    """Date of the last commit touching any of the paths, as YYYY-MM-DD (None if unknown)."""
    result = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%cs", "--", *paths],
                            capture_output=True, text=True)
    return result.stdout.strip() or None


def doc_sources(url):
    """Files in the FairMedFM repository that a documentation page is built from."""
    slug = url[len(DOCS):].strip("/")
    page = f"docs/{slug or 'index'}.md"
    return [page, "src/fairmedfm"] if slug == "api" else [page]


def write_sitemap(entries, path):
    urlset = ET.Element(f"{{{NS}}}urlset")
    for loc, lastmod in entries:
        url = ET.SubElement(urlset, f"{{{NS}}}url")
        ET.SubElement(url, f"{{{NS}}}loc").text = loc
        if lastmod:
            ET.SubElement(url, f"{{{NS}}}lastmod").text = lastmod
    ET.ElementTree(urlset).write(path, encoding="utf-8", xml_declaration=True)


def main(output, docs_repo):
    output, docs_repo = Path(output), Path(docs_repo)
    shutil.copy2(ROOT / "index.html", output / "index.html")
    shutil.copytree(ROOT / "static", output / "static", ignore=shutil.ignore_patterns(".DS_Store"))
    # Search engine ownership files and the IndexNow key, served from the site root.
    for path in (ROOT / "verification").glob("*"):
        if path.name != "README.md":
            shutil.copy2(path, output / path.name)
    (output / ".nojekyll").touch()

    # One sitemap for the whole site, dated by the last change to each page's sources rather than the build date
    # (the site is rebuilt daily).
    ET.register_namespace("", NS)
    docs = [(url.find(f"{{{NS}}}loc").text, None) for url in ET.parse(output / "docs" / "sitemap.xml").getroot()]
    docs = [(loc, last_commit_date(docs_repo, *doc_sources(loc))) for loc, _ in docs]
    entries = [(SITE, last_commit_date(ROOT, "index.html", "static"))] + docs
    write_sitemap(entries, output / "sitemap.xml")
    write_sitemap(docs, output / "docs" / "sitemap.xml")  # a sitemap may only list URLs below its own folder
    (output / "docs" / "sitemap.xml.gz").unlink(missing_ok=True)

    # robots.txt is only read at the host root (nanboy-ronan.github.io/robots.txt), so this copy is informational;
    # submit the sitemap in Google Search Console and Bing Webmaster Tools.
    (output / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n")
    # llms.txt and llms-full.txt are looked up at the site root.
    for name in ("llms.txt", "llms-full.txt"):
        if (output / "docs" / name).exists():
            shutil.copy2(output / "docs" / name, output / name)

    since = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    for loc, lastmod in entries:
        if lastmod and lastmod >= since:
            print(loc)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
