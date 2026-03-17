# Deployment Options Assessment

*AI-generated assessment based on marimo docs, QPSI site analysis, and project constraints.*


## Context

- **Primary audience:** UF medical residents/fellows, med students, staff
- **Secondary audience:** Anyone — we want public accessibility
- **Embedding target:** WordPress/Divi site at https://knowledge.qpsi.med.ufl.edu/
- **Constraint:** ADA compliance required for UF
- **Constraint:** Must be easy to maintain
- **Notebooks:** 10 interactive biostatistics apps, all use Altair + NumPy + Pandas + SciPy


## Option Summary

| Option | Cost | Setup | Maintenance | Package Support | Public Access | Embedding |
|--------|------|-------|-------------|-----------------|---------------|-----------|
| **GitHub Pages (WASM)** | Free | Low | Low | WASM-limited | Yes | iframe |
| **molab (marimo cloud)** | Free | Very low | Very low | Full | Yes | iframe |
| **Self-hosted WASM** | Server cost | Moderate | Moderate | WASM-limited | Configurable | iframe |
| **HiPerGator server** | UF-funded | High | High | Full | UF network only* | iframe |
| **Full server deploy** | Server cost | High | High | Full | Configurable | iframe |

*HiPerGator could be made public but would require IT coordination.


## Detailed Assessment


### 1. GitHub Pages with WASM (Already Implemented)

**How it works:** GitHub Actions exports each notebook to HTML/WebAssembly on push. Deployed as static files on GitHub Pages. Python runs entirely in the viewer's browser via Pyodide.

**Pros:**
- Free forever (GitHub Pages)
- Zero server maintenance — it's static files
- Automatic deployment on git push (CI/CD already set up in this repo)
- Excellent uptime (GitHub's infrastructure)
- Version controlled — rollback is a git revert
- Works for anyone with a browser, no UF network needed

**Cons:**
- 2 GB memory limit per notebook (not an issue for our notebooks — they're lightweight)
- Initial load is slow (~5-10s) as Pyodide + packages download
- Not all Python packages work in WASM (ours do — Altair, NumPy, Pandas, SciPy are all Pyodide-compatible)
- GitHub Pages requires public repo for free tier

**ADA notes:** You control the embedding page. Add `title` attributes to iframes. Consider text summaries alongside interactive content for screen reader users.

**Verdict: Strong primary option.** Already built, free, low maintenance. Our notebooks use only WASM-compatible packages.


### 2. molab (marimo's Cloud)

**How it works:** marimo hosts notebooks on CoreWeave-powered cloud. Push to GitHub, open in molab, click "Share" to get an iframe snippet. Viewers don't need accounts.

**Pros:**
- Simplest setup of all options — literally copy/paste an iframe URL
- Full Python support (not WASM-limited) — server-side execution
- Free (currently)
- marimo's own docs site uses this — proven pattern
- No build step needed

**Cons:**
- Third-party dependency — marimo controls uptime and pricing
- "Free" could change — no SLA or pricing guarantees
- Notebooks are public (fine for us, but worth noting)
- Less control over the environment
- If molab goes down or changes, all embedded notebooks break

**ADA notes:** Same iframe considerations. You have no control over the rendered UI inside molab's iframe.

**Verdict: Excellent supplementary option.** Great for quick sharing and "Open in molab" badges. But relying on it as the *only* deployment path introduces a single point of failure.


### 3. QPSI Knowledgebase with Integrated WASM

**How it works:** Export WASM HTML files and host them directly on the QPSI WordPress site (or iframe from GitHub Pages/molab into WordPress).

**The QPSI site (knowledge.qpsi.med.ufl.edu) runs WordPress with the Divi theme.** Divi's "Code" module or a "Custom HTML" block can hold an iframe. No existing pattern for embedded interactive notebooks on the site — we'd be establishing one.

**Two sub-approaches:**

**(a) iframe from GitHub Pages into WordPress:**
- Simplest. Notebooks live on GitHub Pages, WordPress page just has an `<iframe>`.
- Maintenance is easy — update notebooks in git, WordPress page never changes.
- Requires `allow-scripts allow-same-origin` sandbox attributes.
- Some WordPress security plugins strip iframes — may need to whitelist `github.io`.

**(b) Host WASM HTML directly on WordPress server:**
- Upload exported HTML + assets to WordPress media or a custom directory.
- More control but harder to maintain — must re-upload on every notebook update.
- MIME type configuration needed for `.wasm` files on the UF web server.

**Verdict: Use approach (a) — iframe from GitHub Pages.** Much easier to maintain. The WordPress site just needs a static iframe tag per notebook page.


### 4. HiPerGator Hosting

**How it works:** Run marimo as a server application on UF's HiPerGator supercomputer. Server-side Python execution.

**Pros:**
- Full Python support, no WASM limits
- Powerful compute (useful if notebooks ever need heavy processing)
- UF infrastructure — institutional support

**Cons:**
- Requires HiPerGator allocation/account
- Network access may be restricted to UF VPN (blocks non-UF audience)
- Server must stay running — requires maintenance, monitoring
- Overkill for our lightweight notebooks
- If HiPerGator has maintenance windows, notebooks go down

**Verdict: Not recommended as primary deployment.** Our notebooks are lightweight and don't need server-side compute. The UF network restriction conflicts with our goal of public accessibility. Could be a backup for future notebooks that need heavier computation.


### 5. Full Server Deploy (Docker/Cloud)

**How it works:** Run marimo as an ASGI app behind FastAPI/nginx. Deploy via Docker on any cloud provider.

**Pros:**
- Full Python, no limits
- Complete control
- Can add authentication if needed

**Cons:**
- Ongoing hosting cost
- Must manage servers, scaling, security, SSL, uptime
- Way overkill for 10 static-ish educational notebooks

**Verdict: Not recommended.** Unnecessary complexity and cost for our use case.


## Recommended Strategy

### Primary: GitHub Pages (WASM) — already set up

All 10 notebooks deployed as static WASM apps. Free, automatic, maintainable. This is the canonical source.

### Integration: iframe into QPSI Knowledgebase

Each notebook gets a page on `knowledge.qpsi.med.ufl.edu` with an iframe pointing to the GitHub Pages URL. WordPress/Divi makes this straightforward.

```html
<iframe
  src="https://YOUR-ORG.github.io/qpsi-marimo/notebooks/hypothesis_power.html"
  title="Interactive Biostatistics: Hypothesis Testing, Power, and p-values"
  style="width: 100%; height: 80vh; border: none;"
  loading="lazy"
  sandbox="allow-scripts allow-same-origin allow-downloads allow-popups"
  allow="cross-origin-isolated"
></iframe>
```

### Supplementary: molab badges

Add "Open in molab" badges to the README and notebook pages for users who want the full interactive experience with code editing. This is free and requires zero maintenance.

### Future option: HiPerGator

If we ever build notebooks that need GPU compute, large datasets, or server-side processing, HiPerGator is there. Not needed now.


## ADA Compliance Notes

ADA compliance is a real concern and deserves dedicated attention:

1. **iframe accessibility:** Always include a descriptive `title` attribute on every `<iframe>`. This is how screen readers announce the embedded content.

2. **Keyboard navigation:** Test that users can Tab into and out of the iframe. marimo's UI elements (sliders, checkboxes) should be keyboard-accessible natively.

3. **Color contrast:** Altair charts use color to convey information (e.g., red/green regions). Consider:
   - Using colorblind-friendly palettes
   - Adding text labels alongside color coding
   - Verifying contrast ratios meet WCAG 2.1 AA (4.5:1 for text)

4. **Text alternatives:** For each interactive visualization, the surrounding markdown text already explains what the chart shows. This acts as a de facto text alternative. Could be enhanced with explicit `alt` descriptions.

5. **Screen reader compatibility:** marimo renders standard HTML — sliders are `<input type="range">`, markdown is semantic HTML. This is better than canvas-based solutions. However, Altair charts render as SVG, which can be opaque to screen readers without `<title>` and `<desc>` elements.

6. **Practical recommendation:** Have UF's ADA/IT accessibility team review one deployed notebook before rolling out all 10 on the Knowledgebase. Fix any issues found, then apply the pattern to all notebooks.

7. **Fallback content:** Consider adding a brief text summary below each iframe for users who can't interact with the embedded notebook:
   ```html
   <noscript>
     <p>This interactive notebook requires JavaScript.
     <a href="https://github.com/your-org/qpsi-marimo">View the source code on GitHub.</a></p>
   </noscript>
   ```


## Maintainability Assessment

| Task | Effort |
|------|--------|
| Update a notebook | Edit .py file, push to main. Auto-deploys. |
| Add a new notebook | Create .py file in notebooks/, push. Auto-deploys. Add iframe to WordPress. |
| Update marimo version | Change pin in build.py + notebook headers. Test locally first. |
| WordPress integration | One-time iframe setup per notebook page. Never needs updating. |
| molab badges | One-time README edit. Never needs updating. |

**The GitHub Pages + iframe approach scores highest on maintainability.** The only ongoing work is editing notebook .py files and pushing to git.
