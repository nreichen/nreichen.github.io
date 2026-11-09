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

The site title, menu button and moon button are each a `.logo` holding its
frames (`.logo-frame` children, in order) stacked in one spot. Only the frame
with class `current` shows; the first frame carries it in the HTML so it shows
before any script runs. The script moves `current` back and forth through the
frames, one step every `LOGO_FRAME_MS` (500 ms): 1 2 3 2 1 2 3 … (two frames
just alternate). Logos that start on their own (moon, menu) are offset from
each other by a fraction of a step so they don't change in the same instant.
Visitors with reduced motion turned on see frame 1 held.

The title is the exception (`data-swap="click"`): it holds still until someone
clicks the middle dot in "nathan·reichen", which steps it at once and starts
the animation; another click stops it on whatever frame it's on. The click
target is `.title-dot`, an invisible 28px circle positioned over the drawn
dot (50.2% across, 52% down — the dot sits there in all three drawings; if
the title drawings are redone, re-measure). Clicks elsewhere on the title do
nothing. With reduced motion on, each click moves one step instead.

**Hand-drawn frames.** The owner draws three frames per logo and uploads them
as `1`, `2`, `3` into `images/logos/title/`, `images/logos/moon/`,
`images/logos/menu/` (each folder has a README saying what to upload). The
uploads are the originals; the site uses small copies in a `site/` subfolder,
made with `tools/logo_frames.py` (needs Pillow; usage in the file): crop each to its drawing, center all three on one shared
canvas so they line up, scale (96px tall for the icons, 3× their ~28px
display; 120px for the 40px title), and save as 64-color PNGs (looks
identical, a fifth of the size). By default all frames keep one scale;
`--same-width` (used for the title) scales each to the same width instead,
since the three title drawings were made at different sizes (up to 11%) and
the word would otherwise grow and shrink. If an upload is a photo of
paper rather than a transparent drawing, make the paper transparent first.
In the HTML the frames are `<img class="logo-frame" alt="" draggable="false">`
(the button's `aria-label` names it; the title's frames have `alt` text
instead); `.icon-button img` uses `object-fit: contain`, so a non-square
drawing is fine. Logo images also have the iPhone long-press "Save image"
menu and text selection turned off (`.logo img`).

- **Moon — live (2026-11-08).** `images/logos/moon/site/1–3.png` (~1.5 KB
  each). The drawings are a cream crescent (`#F8F1EA`) with a dark `#333`
  outline on a transparent background, already clean as uploaded. The same
  files work in both modes (outline shows on light; the cream reads on
  dark), so there's no night version.
- **Title — live (2026-11-09).** `images/logos/title/site/1–3.png` (826×120,
  ~14 KB each), "nathan·reichen" hand-lettered in the same cream and dark
  outline, so again no night version. Shown 40px tall (`.site-title img`),
  shrinking on narrow phones to stay between the menu and moon buttons
  (`max-width: calc(100vw - 140px)`, `object-fit: contain`). Each frame has
  `alt="nathan·reichen"`; only the visible one is read out.
- **Menu — placeholder:** two slightly different SVG hamburger drawings in
  the mode's text color. Drawings not uploaded yet.

Before the drawing, the title was text in Cousine, a monospace font bundled
in `fonts/` (Latin subset, 15 KB, SIL Open Font License in
`fonts/cousine-OFL.txt`). It was picked because the owner liked how the title
looked in a screenshot taken on a machine without Courier New, which
substituted Liberation Mono; Cousine renders pixel-identical to it. Cousine
is still used for the Super 8 project titles (no longer preloaded, since
nothing on the first screen uses it).

`images/header-name1.jpg` / `header-name2.jpg` are the old header images and
are no longer used.

## Browser tab (title and icon)

The tab reads "nathan·reichen". The icon is the owner's drawn "n"
(`images/logos/tab/n.png`, live 2026-11-09): cream fill, thick dark outline,
transparent background, so it reads on light and dark tabs without a
separate dark version (checked at 16 and 32px on Chrome's light, light-gray,
dark-gray and near-black tab colors). `tools/tab_icon.py` makes, at the repo
root:

- `favicon.ico` — 16, 32 and 48px, transparent, linked with
  `sizes="16x16 32x32 48x48"`. What Chrome, Edge, Firefox and Safari use.
- `apple-touch-icon.png` (180px) — the "n" on a white square with room
  around it, for iPhone home screens (iOS would fill transparency black).

The old placeholder (a Cousine "n" as `favicon.svg`) was removed; there's no
SVG icon now. If the drawing is redone, upload a new `n` and rerun the script.

## Sidebar

Links: Film (`#film`) and Super 8 (`#super8`). Film is the home page for now
(owner's request, 2026-11-06), so the old Home link (`#`) was dropped — it
showed the same page. Add Home back when there's a real home page. More pages
will be added later.

The closed sidebar is `visibility: hidden` as well as slid off-screen, so Tab
goes from the menu button straight to the page and screen readers skip its
links. The hide is delayed by the 0.3s slide-out
(`transition: left 0.3s ease, visibility 0s linear 0.3s`) and lifted at once
on opening (`transition-delay: 0s` on `.sidebar.open`), so the animation still
plays both ways.

Pages are `<main>` sections in `index.html`, switched by the URL hash in
`showCurrentPage()`: `#super8` shows Super 8; anything else (no hash, `#`,
`#film`, the old `#photography`, typos) shows Film.

## Film page (photo gallery)

Lives inside `index.html` as `<main id="film">`, shown at the bare address
and at `#film` (see Sidebar). No separate HTML page, so the header and
sidebar aren't duplicated.

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
  or on tap for touch screens. Hover and tap count only on the photo itself
  (`.photo-frame`), not the blank part of its square cell — hovering beside a
  photo used to bring up its caption. A photo whose `src` fails to load is dropped
  from the grid and logged to the console.
- Clips play like GIFs (muted, looping, inline) but only while at least a
  quarter of one is on screen, so off-screen clips don't burn battery. With
  reduced motion on they show the poster and a tap plays/pauses them.
- Casual saving is off over photos and clips (owner's request): no
  right-click or Android long-press menu (a `contextmenu` handler on the
  grid), no dragging a photo out, and no iPhone long-press "Save to Photos"
  (`-webkit-touch-callout: none`). Right-click elsewhere on the page works
  normally. This is only a speed bump — screenshots, developer tools, and
  the public repo still give access to the files; a baked-in watermark is
  the only thing that would travel with a download.
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

## Super 8 page (YouTube projects)

`<main id="super8">`, shown at `#super8`. One project per row in a centered
column (max 960px): the embedded YouTube video, then title, when/where (same
format as the photo captions), and a paragraph. No separate "Watch on
YouTube" link (owner's call) — the player's title and logo click through.

- Project list: `super8.js` (`window.SUPER8`), shown in file order. Each entry
  is `{ youtube, title?, season?, year?, location?, blurb?, ratio? }`.
  `youtube` takes any YouTube link or a bare 11-character ID. In `blurb`, a
  blank line (`\n\n`) starts a new paragraph. `ratio: '4 / 3'` makes the frame
  4:3 for videos uploaded without side bars (default 16:9). Empty list shows
  "Super 8 films coming soon."
- Players use YouTube's IFrame API (`https://www.youtube.com/iframe_api`,
  loaded only when the page is opened) on `youtube-nocookie.com`. Each player
  is created when its video comes within 600px of the screen. Videos autoplay
  **muted** (browsers block autoplay with sound; the player's own button
  unmutes), loop, and only play while at least half is on screen — they
  pause when scrolled away or when switching to Film. With reduced motion on
  they never autoplay.
- Testing: this sandbox can't reach YouTube, so tests stub
  `iframe_api` with a fake `YT.Player` that records play/pause calls.

## Gotchas

- **Pages deploys sometimes time out on GitHub's side.** Since the photo
  import (2026-11-06), about half the "pages build and deployment" runs
  fail after 10 minutes in the deploy job with `Current status:
  syncing_files` → `Timeout reached, aborting!`. The build is fine; the
  site just keeps serving the previous version. Re-running the failed job
  has worked every time so far (about a minute). After pushing, check the
  run actually succeeded before telling the owner a change is live.

- Git LFS does not work for site images — GitHub Pages serves the LFS pointer
  file, not the image.

- Keep all page assets on relative or `https://` URLs. Any `http://` asset
  triggers a mixed-content warning even when the page itself is served over
  HTTPS. (Currently clean.)
