"""Combine the project page with the built documentation in the Pages artifact."""
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SITE = "https://nanboy-ronan.github.io/FairMedFM-page/"
ROOT = Path(__file__).resolve().parents[1]
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


def main(output):
    output = Path(output)
    shutil.copy2(ROOT / "index.html", output / "index.html")
    shutil.copytree(ROOT / "static", output / "static", ignore=shutil.ignore_patterns(".DS_Store"))
    (output / ".nojekyll").touch()

    # One sitemap for the whole site: the project page plus every documentation page.
    ET.register_namespace("", NS)
    docs = ET.parse(output / "docs" / "sitemap.xml").getroot()
    urlset = ET.Element(f"{{{NS}}}urlset")
    ET.SubElement(ET.SubElement(urlset, f"{{{NS}}}url"), f"{{{NS}}}loc").text = SITE
    urlset.extend(docs)
    ET.ElementTree(urlset).write(output / "sitemap.xml", encoding="utf-8", xml_declaration=True)

    (output / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n")
    # llms.txt is looked up at the site root.
    shutil.copy2(output / "docs" / "llms.txt", output / "llms.txt")


if __name__ == "__main__":
    main(sys.argv[1])
