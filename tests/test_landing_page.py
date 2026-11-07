"""Checks for the landing page in docs/ (served by GitHub Pages)."""
import re
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"


def test_landing_page_title_and_social_title_have_no_em_dash():
    html = (DOCS / "index.html").read_text(encoding="utf-8")
    head = html.split("</head>", 1)[0]
    for pattern in (r"<title>(.*?)</title>", r'<meta property="og:title" content="(.*?)"', r'<meta name="description" content="(.*?)"'):
        match = re.search(pattern, head, re.S)
        assert match, f"missing {pattern}"
        assert "\u2014" not in match.group(1), f"em dash in {match.group(1)!r}"


def test_sitemap_lists_the_landing_page_with_a_date():
    sitemap = (DOCS / "sitemap.xml").read_text(encoding="utf-8")
    assert re.search(r"<lastmod>\d{4}-\d{2}-\d{2}</lastmod>", sitemap)
