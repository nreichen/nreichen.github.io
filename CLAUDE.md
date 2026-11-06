# nathanreichen.com — site notes

## Hosting

| Layer | Provider | Notes |
|---|---|---|
| Web hosting | **GitHub Pages** | Repo `nreichen/nreichen.github.io` (user-pages repo, serves from `main`) |
| Custom domain | `nathanreichen.com` | Set via the `CNAME` file at repo root — do not delete it, GitHub rewrites it from the Pages settings |
| Domain registrar / DNS | **GoDaddy** (user-reported, not yet verified) | Confirm at https://dcc.godaddy.com/domains — the DNS records live wherever the nameservers point |

The site is plain static HTML (`index.html` + `images/`), no build step. `.nojekyll`
is present, so GitHub serves the files as-is rather than running Jekyll.

## Workflow

Commit and push directly to `main` (owner's preference since 2026-11-06) — no
feature branches or pull requests. `main` is what GitHub Pages serves, so
every push is live within about a minute. Before pushing, test in a browser:
serve the repo with `python3 -m http.server` and check light and dark mode
(`prefers-color-scheme`) at desktop and phone widths.

The owner uploads images through github.com ("Add files via upload"), which
commits straight to `main`, so pull before starting work.

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

## Background picture and light/dark mode

The site has a light and a dark version. The visitor's device setting
(`prefers-color-scheme`) picks one until they click the night mode toggle (the
moon, top right). That sets `data-theme="light"|"dark"` on
`<html>` and saves it in `localStorage` (`theme`); a small script at the top of
`<head>` re-applies it before the page draws on later visits. The colors and
picture for each are CSS variables at the top of `index.html`'s `<style>` (the
dark values appear twice: once for the device setting, once for the toggle):

| | Light (default) | Dark |
|---|---|---|
| Picture | `images/background-light.jpg` | `images/background-dark.jpg` |
| Text and menu icon | `#111` (near-black) | white |
| Color while the picture loads | white | `#222` |

The picture covers the whole window behind every page, fixed in place while
scrolling (a `position: fixed` layer on `body::before`, since iOS ignores
`background-attachment: fixed`). It's cropped to fill the screen. Both
pictures are the same misty mountain ridge (day and night versions, from the
owner's film scans), with the main peak about a third of the way across; the
crop is anchored at 35% horizontally so phones and portrait tablets, which only
see a narrow vertical strip, keep that peak in view. Wide screens show the full
width and crop top and bottom instead. If you swap in a differently composed
picture, revisit that 35%. If a picture file is missing, that mode falls back
to its plain color. Pictures load on every visit, so keep them
around 2560px wide and ~1 MB or less — film grain compresses poorly, and
grayscale scans should be saved as single-channel JPEGs.

The sidebar has no panel: its links sit directly on the background in the
mode's text color, with the same faint shadow as the icons so they stay
readable over gallery photos.

## Logos (title, menu, moon)

The site title, menu button and moon button are each a `.logo` holding two
`.logo-frame` children stacked in one spot. A script toggles `.show-alt` on
each logo on its own random timer (`LOGO_SWAP_MIN_MS`–`LOGO_SWAP_MAX_MS`,
300–1500 ms), so the owner's eventual hand-drawn pairs will look like they're
moving. Visitors with reduced motion turned on see them hold still.

The title is the exception (`data-swap="click"`): it holds still until someone
clicks the middle dot in "nathan·reichen", which starts the swapping; another
click stops it. The dot (`.title-dot`) has extra invisible padding so it's easy
to hit. With reduced motion on, each click changes the font once instead.

Current placeholders: the title is "nathan·reichen" (middle dot, U+00B7) in
Cousine, a monospace font bundled in `fonts/` (Latin subset, 15 KB, SIL Open
Font License in `fonts/cousine-OFL.txt`, preloaded in `<head>`), alternating
with Georgia when the dot is clicked. Cousine was picked because the owner
liked how the title looked in a screenshot taken on a machine without Courier
New, which substituted Liberation Mono; Cousine renders pixel-identical to it; the menu and moon are two slightly different SVG drawings each, in the
mode's text color. To swap in drawings, replace each pair with two `<img>`s
keeping `class="logo-frame"` (and give the title's images `alt` text).
`images/header-name1.jpg` / `header-name2.jpg` are the old header images and
are no longer used.

## Sidebar

Links: Home (`#`) and Film (`#film`). More pages will be added later.

## Film page (photo gallery)

Lives inside `index.html` as a hidden `<main id="film">`, shown when the URL
hash is `#film` (the sidebar's Film link). The page's first address,
`#photography`, still works. Home is `#`. No separate HTML page, so the header
and sidebar aren't duplicated.

- Photo list: `photos.js` (`window.PHOTOS`), displayed in file order. Each
  entry is `{ src, season, year, location?, poster? }`. `src` is a repo path
  under `images/photography/` or a full `https://` URL from an image host.
  A `src` ending in `.mp4` is a clip (see below) and `poster` is its still.
- Current contents (imported 2026-11-06): 231 film photos and 29 RETO "3D"
  clips, newest first. Files are named by their 5-digit number from the Drive
  folder (`00450.jpg` is `00450 …` in Drive); the numbers count by tens from
  00010 = newest. Where Google Photos had an `-edited` copy, the site uses it.
  Display order comes from `photos.js`, not the file names, so a newer photo
  can go at the top under any name.
- Site copies are made from the Drive originals: EXIF rotation baked in
  (00780–00810 were stored sideways with a rotate flag), long edge 1600px,
  progressive JPEG quality 80, metadata stripped (~330 KB each). Clips are
  silent H.264 MP4 (CRF 23, `+faststart`, ~400 KB) with a first-frame poster
  JPEG of the same number.
- Captions are season + year from each photo's Google Takeout date (read in
  Ann Arbor time). For some scans that may be the upload date rather than
  when the photo was taken — the owner is correcting them, and adding
  locations, in a caption sheet.
- 2-column grid of square cells spanning the full window width.
  `--photo-spacing` (20px) sets the gap between cells and the
  left/right/bottom margins alike. Each photo is fitted uncropped and
  centered in its square, long edge filling it, so vertical and horizontal
  photos show at the same size (the short side gets white space). Photos load
  8 at a time as the bottom nears the screen (`PHOTOS_PER_BATCH`).
- Caption ("Fall 2024 · Ann Arbor, MI") fades in on hover, on keyboard focus,
  or on tap for touch screens. A photo whose `src` fails to load is dropped
  from the grid and logged to the console.
- Clips play like GIFs (muted, looping, inline) but only while at least a
  quarter of one is on screen, so off-screen clips don't burn battery. With
  reduced motion on they show the poster and a tap plays/pauses them.
- The menu and moon buttons are `position: fixed` so they stay reachable
  while scrolled down the gallery.

### Where the photos come from (Google Drive)

In the owner's Drive, under **Film**:

- **Film Photos** — the originals from a Google Photos Takeout, renamed
  `NNNNN original-name` (5 digits, newest first, counting by tens; edited
  copies share their original's number). Photos and clips only.
- **Film Photos – Takeout data** — the Takeout `.supplemental-metadata.json`
  files (dates, etc.) moved out of the way.
- **Film Favorites** — the owner's picks (empty so far; what favorites do
  on the site is undecided).

## Gotchas

- Git LFS does not work for site images — GitHub Pages serves the LFS pointer
  file, not the image.

- Keep all page assets on relative or `https://` URLs. Any `http://` asset
  triggers a mixed-content warning even when the page itself is served over
  HTTPS. (Currently clean.)
