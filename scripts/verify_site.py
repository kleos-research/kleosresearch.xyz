#!/usr/bin/env python3
"""Dependency-free release-surface checks for the static Kleos site."""

from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
SOCIAL_IMAGE = "https://kleosresearch.xyz/assets/kaleidoscope-og.png"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class Document(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self._in_title = False
        self.meta: dict[str, str] = {}
        self.links: list[str] = []
        self.json_ld: list[str] = []
        self._in_json_ld = False
        self._json_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            key = values.get("name") or values.get("property")
            if key:
                self.meta[key] = values.get("content", "")
        elif tag == "link":
            href = values.get("href")
            if href:
                self.links.append(href)
        elif tag == "a":
            href = values.get("href")
            if href:
                self.links.append(href)
        elif tag == "script" and values.get("type") == "application/ld+json":
            self._in_json_ld = True
            self._json_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._in_json_ld:
            self.json_ld.append("".join(self._json_parts))
            self._in_json_ld = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        if self._in_json_ld:
            self._json_parts.append(data)


def fail(message: str) -> None:
    raise AssertionError(message)


def parse_document(path: Path) -> Document:
    document = Document()
    document.feed(path.read_text(encoding="utf-8"))
    return document


def local_target(href: str) -> Path | None:
    parsed = urlparse(href)
    if parsed.scheme or parsed.netloc or not parsed.path.startswith("/"):
        return None
    path = parsed.path
    if path == "/":
        return ROOT / "index.html"
    relative = path.lstrip("/")
    if path.endswith("/") or "." not in Path(relative).name:
        return ROOT / relative / "index.html"
    return ROOT / relative


def expect_metadata(path: Path, canonical: str, title: str, types: set[str]) -> None:
    document = parse_document(path)
    if document.title.strip() != title:
        fail(f"{path}: expected title {title!r}, got {document.title.strip()!r}")
    required = {
        "description": None,
        "og:type": "website",
        "og:url": canonical,
        "og:image": SOCIAL_IMAGE,
        "og:image:width": "1200",
        "og:image:height": "630",
        "og:image:alt": "Kaleidoscope — local memory for agents",
        "twitter:card": "summary_large_image",
        "twitter:image": SOCIAL_IMAGE,
        "twitter:image:alt": "Kaleidoscope — local memory for agents",
    }
    for name, expected in required.items():
        value = document.meta.get(name)
        if not value:
            fail(f"{path}: missing {name}")
        if expected and value != expected:
            fail(f"{path}: {name} must be {expected!r}, got {value!r}")
    if canonical not in document.links:
        fail(f"{path}: missing canonical link {canonical}")
    if not document.json_ld:
        fail(f"{path}: missing JSON-LD")
    observed_types: set[str] = set()
    for payload in document.json_ld:
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as error:
            fail(f"{path}: invalid JSON-LD: {error}")
        nodes = data.get("@graph", [data])
        observed_types.update(node.get("@type", "") for node in nodes)
    if not types.issubset(observed_types):
        fail(f"{path}: JSON-LD missing {sorted(types - observed_types)}")
    for href in document.links:
        target = local_target(href)
        if target and not target.is_file():
            fail(f"{path}: broken local link {href} -> {target.relative_to(ROOT)}")


def verify_sitemap() -> None:
    root = ElementTree.parse(ROOT / "sitemap.xml").getroot()
    namespace = {"site": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locations = {node.text for node in root.findall("site:url/site:loc", namespace)}
    expected = {
        "https://kleosresearch.xyz/",
        "https://kleosresearch.xyz/products/",
        "https://kleosresearch.xyz/research/",
        "https://kleosresearch.xyz/notes/",
        "https://kleosresearch.xyz/lab/",
        "https://kleosresearch.xyz/privacy/",
        "https://kleosresearch.xyz/terms/",
    }
    if locations != expected:
        fail(f"sitemap.xml: expected {sorted(expected)}, got {sorted(locations)}")


def main() -> int:
    image = ROOT / "assets" / "kaleidoscope-og.png"
    if not image.is_file() or not image.read_bytes().startswith(PNG_SIGNATURE):
        fail("assets/kaleidoscope-og.png must be a PNG")
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "Sitemap: https://kleosresearch.xyz/sitemap.xml" not in robots:
        fail("robots.txt: missing canonical sitemap")
    expect_metadata(
        ROOT / "index.html",
        "https://kleosresearch.xyz/",
        "Kleos — AI research lab",
        {"Organization"},
    )
    expect_metadata(
        ROOT / "products" / "index.html",
        "https://kleosresearch.xyz/products/",
        "Products — Kleos",
        {"WebPage", "SoftwareApplication"},
    )
    verify_sitemap()
    print("Kleos static release surface is valid.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
