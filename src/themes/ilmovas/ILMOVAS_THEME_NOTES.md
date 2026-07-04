# Ilmovas Janeway Theme Notes

Upstream-sync map for the **ilmovas** full custom theme (Ilmovas / إلموفاس).
Use this file when merging Janeway core or OLH theme updates: only **Modified** templates
and assets need manual conflict review.

---

## 1. Base fork

| Item | Value |
|------|--------|
| **Upstream** | OLH theme (`bbkolh/olh-theme` on Bitbucket) |
| **OLH commit pin** | **Unknown** — original fork had no git tag, branch, or commit hash in README. |
| **Effective baseline** | **2026-07-04** — theme frozen for Ilmovas production deploy under directory `ilmovas`. |
| **Janeway version pin** | **Record on server at deploy time** — run `python3 manage.py --version` (or check `requirements.txt` / Docker image tag) and append below when known. |
| **Theme directory name** | `ilmovas` (Janeway path: `themes/ilmovas/`, static namespace: `static/ilmovas/`) |
| **Customization scope** | Full theme — intentional Ilmovas re-skin, not a minimal sub-theme |

---

## 2. Production fixes applied (2026-07-04)

### Fix 1 — `local-fonts.css` (path **b**: create file)

- **Problem:** `templates/core/base.html` referenced `{% static 'ilmovas/css/local-fonts.css' %}` but the file did not exist.
- **Action:** Created `assets/css/local-fonts.css` with self-hosted `@font-face` for:
  - **Tajawal** (300–800) → `assets/fonts/tajawal/*.woff2`
  - **Material Symbols Outlined** → `assets/fonts/material-symbols/MaterialSymbolsOutlined.ttf` (downloaded for self-hosting; was previously only available via Google CDN in `app.scss`)
- **Build:** Added `process_standalone_css()` in `build_assets.py` to copy `assets/css/` → `static/ilmovas/css/`.

### Fix 2 — Remove external CDN imports from SCSS

- **Problem:** `assets/scss/app.scss` imported Google Fonts (Tajawal, Material Symbols) and Bootstrap CDN (Font Awesome).
- **Action:**
  - Replaced Tajawal CDN with `@import 'fonts'` → new `assets/scss/_fonts.scss` (local Tajawal only).
  - Removed Material Symbols CDN from SCSS (icons load via `local-fonts.css` on Tailwind pages using `core/base.html`).
  - Removed Font Awesome CDN from SCSS bundle (Font Awesome loaded separately in `base.html` via local `font-awesome.min.css`).
- **Resolved (2026-07-04 pass 2):** Font Awesome binaries downloaded; see §5.

### Fix 3 — Delete unreferenced legacy templates

| File | Reason |
|------|--------|
| `templates/core/nav.html` | Not included by `base.html` (inline Tailwind nav). No references anywhere in theme. |
| `templates/journal/articles.html` | Marked deprecated (v1.5.1); superseded by `journal/article_list.html`. Zero references in theme. |

### Fix 4 — Repo hygiene

- Expanded `.gitignore`: `__pycache__/`, `*.pyc`, `*.pyo`, `.DS_Store`, `assets/scss/app.css` (stale compile artifact).
- Deleted stale `assets/scss/app.css` (contained old CDN URLs and a failed compile error).
- No committed `__pycache__` directories were present.

---

## 3. Templates modified for Ilmovas (conflict-review list)

Identified by Ilmovas-specific markers: Tailwind layout (`max-w-[1280px]`), brand colors (`#0D4F3C`, `#C4922A`), `material-symbols-outlined`, `gold-border-top`, `bg-ivory`, `ilmovas` static paths, Tajawal, RTL-aware markup.

| Template | Notes |
|----------|--------|
| `templates/core/base.html` | **Primary shell** — Tailwind, RTL/LTR, inline nav/footer, self-hosted assets |
| `templates/core/a11y.html` | Arabic accessibility page, Tailwind layout |
| `templates/core/accounts/public_profile.html` | Tailwind profile page |
| `templates/cms/page.html` | Tailwind CMS pages |
| `templates/journal/article.html` | Full article view (Tailwind); self-hosted MathJax 3.2.2 CHTML subset |
| `templates/journal/article_list.html` | Article listing (Tailwind) |
| `templates/journal/submissions.html` | Submission landing (Tailwind, Arabic copy) |
| `templates/journal/search.html` | Search results (Tailwind) |
| `templates/journal/issue.html` | Single issue view (Tailwind) |
| `templates/journal/issues.html` | Issue archive (Tailwind) |
| `templates/journal/contact.html` | Contact form (Tailwind) |
| `templates/journal/editorial_team.html` | Editorial team (Tailwind) |
| `templates/journal/homepage_elements/featured.html` | Featured article hero |
| `templates/journal/homepage_elements/issue_block.html` | Latest issue block |
| `templates/journal/homepage_elements/article_list_item.html` | Homepage article row |
| `templates/elements/journal/share.html` | Share buttons |
| `templates/elements/journal/article_list_filters.html` | Filter UI |
| `templates/elements/section_block.html` | Section metadata block |
| `templates/500.html` | Self-contained error page — local CSS only, no external scripts |

### SCSS / assets modified (not templates)

| File | Notes |
|------|--------|
| `assets/scss/app.scss` | CDN removed; Tajawal local; Ilmovas colors in body/RTL |
| `assets/scss/_variables.scss` | Ilmovas green/gold/ivory palette |
| `assets/scss/_settings.scss` | Foundation palette → `#0D4F3C` / `#C4922A` |
| `assets/scss/_fonts.scss` | **New** — local Tajawal `@font-face` |
| `assets/css/local-fonts.css` | **New** — Tajawal + Material Symbols for `base.html` |
| `assets/fonts/material-symbols/MaterialSymbolsOutlined.ttf` | **New** — self-hosted icon font |
| `assets/fonts/fontawesome-webfont.{woff2,woff,ttf,eot}` | **Fixed** — real Font Awesome 4.6.3 binaries (were 0-byte placeholders) |
| `assets/js/mathjax/` | **Wave 2** — MathJax 3.2.2 CHTML subset (~1.6 MB); was 2.7.7 full (~178 MB) |
| `build_assets.py` | `process_standalone_css()`, `process_vendor_assets()`, `process_mathjax()` |

---

## 4. Templates likely OLH verbatim or legacy (lower merge priority)

These extend `core/base.html` or use Foundation (`row`, `columns`, `top-bar`) without Tailwind/Ilmovas markers. Review only if Janeway changes underlying view context or OLH updates the same file.

- **Press** (13 templates): `press/*` — Foundation layout
- **Repository** (11 templates): `repository/*` — Foundation layout
- **Core accounts (legacy):** `core/login.html`, `core/accounts/register.html`, `edit_profile.html`, etc.
- **Journal (legacy):** `journal/index.html`, `authors.html`, `collections.html`, `full-text-search.html`, `become_reviewer.html`, `keyword.html`, `keywords.html`, `print.html`, `issue_display.html`, most `homepage_elements/*` except those listed above
- **Elements** (~30 files): submission forms, modals, citation blocks, Foundation partials
- **Errors:** `403.html`, `404.html` (500 partially customized)

---

## 5. Deploy-prep fixes (2026-07-04, second pass)

### Rename `ilmovas_new` → `ilmovas`

- Theme directory and all static paths now use `ilmovas` (no `ilmovas_new` references remain).
- Janeway setting: set theme to **`ilmovas`**.

### Font Awesome binary fonts

- **Problem:** `assets/font-awesome/fonts/` and `assets/fonts/` had 0-byte placeholder files; only `.svg` was real.
- **Fix:** Downloaded Font Awesome **4.6.3** binaries (`.woff2`, `.woff`, `.ttf`, `.eot`) into `assets/font-awesome/fonts/`, copied to `assets/fonts/` for `process_fonts()`.
- **CSS path:** `font-awesome.min.css` uses `url('../fonts/fontawesome-webfont.woff2')` — correct when CSS is at `static/ilmovas/css/` and fonts at `static/ilmovas/fonts/`.
- **Build:** Added `process_vendor_assets()` to copy `font-awesome.min.css`, `toastr.min.css`, jQuery, toastr, tailwind-cdn into static.

### `500.html` — removed all external CDN

| Removed | Replacement |
|---------|-------------|
| cdnjs toastr CSS | Removed (page has no toastr calls) |
| Adobe Typekit | Removed |
| cdnjs jQuery 2.2.4 | Removed (no JS needed) |
| cdnjs Foundation 6.5.1 | Removed (no JS needed) |
| — | Self-contained RTL page with local `local-fonts.css` + `app.css` + inline minimal styles |

### MathJax — self-hosted (updated Wave 2, 2026-07-04)

- **Decision:** Self-host (Ilmovas publishes scientific/Arabic academic content; math may be required offline).
- **Package:** MathJax **3.2.2** CHTML subset (`tex-mml-chtml` component), replacing 2.7.7 full tree.
- **Loader:** Inline `window.MathJax` config + deferred `es5/tex-mml-chtml.js` in `templates/journal/article.html`.
- **Paths kept in theme:**
  - `assets/js/mathjax/es5/tex-mml-chtml.js`
  - `assets/js/mathjax/es5/output/chtml/fonts/tex.js`
  - `assets/js/mathjax/es5/output/chtml/fonts/woff-v2/*.woff` (23 font files)
- **Size:** ~1.6 MB in `assets/js/mathjax/` (was ~178 MB with MathJax 2.7.7).
- **Tradeoff:** AsciiMath (`AM`) from old `TeX-MML-AM_CHTML` config is **not** included in `tex-mml-chtml`; TeX + MathML only. Verify on server with a real article containing `$...$`, `\[...\]`, and MathML.
- **Server verification required:** Math rendering must be tested on production/staging with a real article after deploy.

### OLH / Janeway version pin

See §1 **Effective baseline 2026-07-04**. On deploy, record the running Janeway version here:

```
Janeway version at deploy: (fill in after server check)
OLH upstream commit: unknown — diff the 19 modified templates in §3 on future OLH sync
```

---

## 6. Known pending work

| Item | Severity |
|------|----------|
| **Press & Repository** still on Foundation — not yet migrated to Tailwind | Medium (visual inconsistency) |
| **Altmetric badge** in `article.html` — still loads `embed.js` from Altmetric CloudFront (third-party service, not a font/CDN dependency) | Low |
| **README.md** — still says "OLH Theme Repository"; no ilmovas install docs | Low |
| **MathJax size** | ~~178 MB~~ **Resolved Wave 2** — MathJax 3.2.2 CHTML subset ~1.6 MB | Done |
| **Template slimming** | 85 VERBATIM? templates vs 19 MODIFIED — see §8 Wave 3; do not delete until fallback chain verified | Medium |

---

## 7. Build & deploy checklist

```bash
# From Janeway src/
python3 manage.py build_assets
```

Ensures: SCSS → `static/ilmovas/css/app.css`, JS bundle, fonts (Tajawal, Material Symbols, Font Awesome), vendor CSS/JS, **MathJax**, images, **`local-fonts.css`**, then `collectstatic`.

Set theme to **`ilmovas`** in Janeway settings. Theme path: `src/themes/ilmovas/`.

---

## 8. Pre-deploy size trim — three waves (2026-07-04)

Baseline before trim: **193 MB**. After Waves 1+2: **6.2 MB**.

### Wave 1 — Safe trim (no functional loss)

| Action | Detail |
|--------|--------|
| **Removed** `assets/img/default_carousel/` (~9.6 MB) | OLH demo carousel images; journals upload their own. `templates/core/news/index.html` references Janeway model fields (`default_large_image`, `default_carousel_image`), not these files. |
| **Removed** `assets/img/sample/` (~108 KB) | OLH demo issue cover. `templates/elements/journal/issue_list.html` uses `common/img/sample/issue_cover.png` (Janeway core static), not theme assets. |
| **Removed** duplicate FA binaries under `assets/font-awesome/fonts/` | Canonical deploy path: `assets/fonts/` → `static/ilmovas/fonts/` via `process_fonts()`. `font-awesome.min.css` uses `../fonts/` — resolves correctly when CSS is at `static/ilmovas/css/`. |
| **Removed** 0-byte `FontAwesome.otf` | From both `assets/fonts/` and `assets/font-awesome/fonts/`. |
| **Removed orphan JS** | `jq-ui.min.js`, `epub.min.js`, `zip.min.js`, `jq-ui-timepicker.js`, `tailwind-3.4.17.js` (0 template refs). |
| **Removed** `assets/js/jquery-te-1.4.0.min.js` | Theme copy orphan; `templates/elements/jqte.html` loads from `common/js/`. |
| **Removed** `assets/what-input/` (~76 KB) | 0 template refs; not imported in `app.scss`. |
| **KEPT** `assets/js/toastr.js` | 0 direct template refs but **required** by `build_assets.py` `process_js()` bundle. |
| **KEPT** `assets/motion-ui/` + `assets/foundation-sites/` | Imported in `assets/scss/app.scss` (`@import 'motion-ui'`). **Deferred to future Wave 3** — do not remove without dropping SCSS imports and verifying Foundation pages. |

**build_assets.py references:** `process_images()` copies whatever exists under `assets/img/` — no hard-coded demo paths. Comment added in `process_images()`.

**Size after Wave 1:** 183 MB (MathJax 2.7.7 still present).

### Wave 2 — MathJax 3.x CHTML subset

| Step | Detail |
|------|--------|
| **Removed** entire `assets/js/mathjax/` MathJax 2.7.7 tree (~178 MB) | |
| **Installed** MathJax 3.2.2 via `npm pack mathjax@3.2.2`, pruned to CHTML subset | See MathJax section above for file list. |
| **Updated** `templates/journal/article.html` | MathJax 3 loader API with inline config + `defer` on `tex-mml-chtml.js`. Code comment added. |
| **Updated** `build_assets.py` `process_mathjax()` | Docstring documents subset paths; copy logic unchanged (full `assets/js/mathjax/` tree). |

**Size after Wave 2:** 6.2 MB total theme; MathJax subset 1.6 MB.

**Post-deploy verification:** Open an article with inline `$x^2$`, display `\[...\]`, and MathML; confirm fonts load from `static/ilmovas/js/mathjax/es5/output/chtml/fonts/woff-v2/`.

### Wave 3 — Template classification (INVESTIGATION ONLY — no deletions)

Automated marker scan (`ilmovas`, `tajawal`, `#0D4F3C`, `#C4922A`, `material-symbols`, Tailwind layout classes, etc.):

| Category | Count |
|----------|-------|
| **MODIFIED** | **19** |
| **VERBATIM?** | **85** |

**MODIFIED (keep — Ilmovas custom work):**

- `templates/500.html`
- `templates/cms/page.html`
- `templates/core/a11y.html`
- `templates/core/accounts/public_profile.html`
- `templates/core/base.html`
- `templates/elements/journal/article_list_filters.html`
- `templates/elements/journal/share.html`
- `templates/elements/section_block.html`
- `templates/journal/article.html`
- `templates/journal/article_list.html`
- `templates/journal/contact.html`
- `templates/journal/editorial_team.html`
- `templates/journal/homepage_elements/article_list_item.html`
- `templates/journal/homepage_elements/featured.html`
- `templates/journal/homepage_elements/issue_block.html`
- `templates/journal/issue.html`
- `templates/journal/issues.html`
- `templates/journal/search.html`
- `templates/journal/submissions.html`

**VERBATIM? (85 templates — candidates for revert-to-`clean` inheritance after fallback-chain verification):**

All remaining templates under `templates/` including: `403.html`, `404.html`, press (13), repository (11), legacy core accounts, legacy journal pages (`index.html`, `authors.html`, `collections.html`, etc.), and ~30 Foundation `elements/` partials.

**Do NOT delete any VERBATIM template until:**

1. Janeway theme fallback chain is confirmed for `ilmovas` (full theme, not sub-theme — may differ from prior sub-theme advice).
2. Each candidate template is diffed against OLH/clean upstream.
3. Manual QA on affected pages (submission forms, press, repository, legacy account flows).

**Deferred (Wave 3 future):** Evaluate dropping `motion-ui` / trimming `foundation-sites` if Tailwind migration completes for all Foundation pages.
