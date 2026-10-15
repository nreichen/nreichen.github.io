# nathanreichen.com — site notes

## Hosting

| Layer | Provider | Notes |
|---|---|---|
| Web hosting | **GitHub Pages** | Repo `nreichen/nreichen.github.io` (user-pages repo, serves from `main`) |
| Custom domain | `nathanreichen.com` | Set via the `CNAME` file at repo root — do not delete it, GitHub rewrites it from the Pages settings |
| Domain registrar / DNS | **GoDaddy** (user-reported, not yet verified) | Confirm at https://dcc.godaddy.com/domains — the DNS records live wherever the nameservers point |

The site is plain static HTML (`index.html` + `images/`), no build step. `.nojekyll`
is present, so GitHub serves the files as-is rather than running Jekyll.

## DNS records GitHub Pages expects

GitHub Pages reports **"DNS check successful"** — the A records below are
correct and GoDaddy forwarding is NOT in play.

Apex (`nathanreichen.com`) — four A records, **not** a GoDaddy "Forwarding" rule:

    185.199.108.153
    185.199.109.153
    185.199.110.153
    185.199.111.153

Optionally `www` as a CNAME to `nreichen.github.io`.

**GoDaddy Domain Forwarding must be off.** GoDaddy's forwarding serves the
redirect over plain HTTP from its own parking servers, which permanently
breaks HTTPS for a GitHub Pages custom domain. It is the most common cause
of a "Not Secure" badge on this setup.

## HTTPS

Pages settings live at
**https://github.com/nreichen/nreichen.github.io/settings/pages** — the
*repository* Settings tab, not the account-level `github.com/settings/pages`
page. The account-level one only handles "Verified domains", an optional
anti-takeover feature that is unrelated to certs and HTTPS.

GitHub provisions a free Let's Encrypt cert for the custom domain once DNS
resolves to the IPs above. Then tick **Enforce HTTPS** so `http://` redirects
to `https://`.

**Resolved 2026-10-15.** The cert had never been issued (the checkbox read
"a certificate has not yet been issued" for ~18 months despite DNS passing).
Removing and re-adding the custom domain in Pages settings retriggered
provisioning and fixed it — visible on `main` as a `Delete CNAME` /
`Create CNAME` commit pair. GitHub does not retry a failed provisioning job on
its own, so that is the first thing to try if it ever recurs.

If remove/re-add doesn't work, check the apex for:

- A **CAA record** that doesn't authorize `letsencrypt.org` — blocks issuance
  silently.
- Any **AAAA record** — Pages has no IPv6 on the apex, and Let's Encrypt
  prefers IPv6 when one exists, so a stale AAAA breaks validation while
  GitHub's DNS check (A records only) still passes.

## Photography page

Lives inside `index.html` as a hidden `<main id="photography">`, shown when the
URL hash is `#photography` (the sidebar link). Home is `#`. No separate HTML
page, so the header and sidebar aren't duplicated.

- Photo list: `photos.js` (`window.PHOTOS`), displayed in file order. Each
  entry is `{ src, season, year, location? }`. `src` is a repo path under
  `images/photography/` or a full `https://` URL from an image host.
- 2-column grid spanning the full window width. `--photo-spacing` (20px) sets
  the gap between photos and the left/right/bottom margins alike, so all
  spacing is equal. Photos load 8 at a time as the bottom nears the screen
  (`PHOTOS_PER_BATCH`). Photos keep their own proportions — nothing is
  cropped — so a portrait next to a landscape leaves white space under the
  landscape.
- Caption ("Fall 2024 · Ann Arbor, MI") fades in on hover, on keyboard focus,
  or on tap for touch screens. A photo whose `src` fails to load is dropped
  from the grid and logged to the console.
- The menu icon is `position: fixed` so the sidebar stays reachable while
  scrolled down the gallery.

## Gotchas

- The menu icon is broken: it starts on `/api/placeholder/40/40` and cycles
  through `images/menu/menu-icon1.jpg` / `menu-icon2.jpg`, none of which exist
  in the repo, so it renders as the alt text "Menu" (still clickable).
- Git LFS does not work for site images — GitHub Pages serves the LFS pointer
  file, not the image.

- Keep all page assets on relative or `https://` URLs. Any `http://` asset
  triggers a mixed-content warning even when the page itself is served over
  HTTPS. (Currently clean.)
