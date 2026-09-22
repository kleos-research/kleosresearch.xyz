# kleosresearch.xyz

The website of Kleos Research, an AI research lab:
[kleosresearch.xyz](https://kleosresearch.xyz). It introduces the lab, lists its
research and notes, and links to its two products,
[0xCopilot](https://copilot.kleosresearch.xyz) and
[Kaleidoscope](https://memory.kleosresearch.xyz).

## What is here

The site is plain HTML. There is no build step and nothing to install.

| Page | File |
| --- | --- |
| Home | `index.html` |
| Research, with the published paper | `research/` |
| Notes | `notes/index.html` |
| Products | `products/index.html` |
| About the lab | `lab/index.html` |
| Privacy and terms | `privacy/index.html`, `terms/index.html` |
| Summaries for language models | `llms.txt`, `llms-full.txt` |
| Sitemap and crawler rules | `sitemap.xml`, `robots.txt` |
| Icons and the social preview image | `favicon*`, `apple-touch-icon.png`, `assets/` |

Each page is a complete document with its own styles, header and footer. To
change the navigation, the footer or the colours, edit every page.

Every page also carries a `virtual-protocol-site-verification` meta tag. It
proves to the Virtuals Protocol listing linked in the footer that Kleos owns
this domain, so keep it on every page.

## Preview it locally

From the repository root, serve the folder with any static file server, for
example:

```sh
python3 -m http.server 8000
```

Then open http://localhost:8000. To check page titles, social metadata, local
links and the sitemap:

```sh
python3 scripts/verify_site.py
```

## How it deploys

GitHub Pages serves the `main` branch at kleosresearch.xyz. The `CNAME` file
sets the domain. Nothing is built or checked on the way, so merging to `main`
publishes the change as it is.

## Licence

There is no open-source licence. The text, design and research on the site
belong to Kleos Research; the [terms](https://kleosresearch.xyz/terms/) say what
you may quote and reuse.
