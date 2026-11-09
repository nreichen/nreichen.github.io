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
| Text (Super 8 page etc.) | `#333`, the logos' dark outline (`--logo-ink`) | `#F8F1EA`, the logos' cream fill (`--logo-cream`) |
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

Text colors come from the owner's drawings (owner's request, 2026-11-09):
`--logo-ink` and `--logo-cream` are defined once at the top of the `:root`
block, and `--text-color` points at one or the other per mode. Photo
captions are always `--logo-cream`, since they sit on a dark band in both
modes.

The sidebar has no panel: its links sit directly on the background, drawn
like the title in **both** modes (owner's request, 2026-11-09): cream
letters (`--logo-cream`) with a dark `--logo-ink` outline, semibold 20px,
plus the title's faint drop shadow. The outline is a 3px
`-webkit-text-stroke` with `paint-order: stroke fill`, so the stroke sits
behind the letters and only its outer 1.5px shows (Chrome 123+, Safari,
Firefox). Readable over gallery photos too. Opening the menu at the top of a page slides
the content down below the links (see Sidebar), so they sit on clear
mountains there.

## Logos (title, menu, moon)

The site title, menu button and moon button are each a `.logo` holding its
frames (`.logo-frame` children, in order) stacked in one spot. Only the frame
with class `current` shows; the first frame carries it in the HTML so it shows
before any script runs. The script moves `current` back and forth through the
frames, one step every `LOGO_FRAME_MS` (500 ms): 1 2 3 2 1 2 3 … (two frames
just alternate). All three start on their own when the page loads, each
offset by a third of a step (moon, then menu, then title) so they don't
change in the same instant. Visitors with reduced motion turned on see
frame 1 held.

The title used to hold still until someone clicked the middle dot; since
2026-11-09 it plays on its own like the others (owner's request).

**The title is the home link** (owner's request, 2026-11-09). Its frames sit
in `<a href="./" class="title-link logo">` inside the `<h1 class="site-title">`
(the `.logo` class moved to the link, since the frames must be the logo's
direct children). A click handler goes home without reloading: it drops any
`#super8` etc. from the address with `history.pushState` (so Back returns to
it), calls `showCurrentPage()`, closes the sidebar if open, and scrolls to the
top (smoothly, unless reduced motion). Cmd/Ctrl/Shift/middle clicks are left
to the browser, so they open the plain `./` address in a new tab. "Home" is
Film for now; when there's a real home page, the title goes there.

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
- **Menu — live (2026-11-09).** `images/logos/menu/site/1–3.png` (120×96,
  ~2 KB each), three hand-drawn bars in the same cream and dark outline;
  same scale for all frames (they differ more in width than height). Still
  turns 90° when the sidebar opens (`.menu-icon.open`).

All three logos and the tab icon are now the owner's drawings; the SVG
placeholders are gone.

Before the drawing, the title was text in Cousine, a monospace font (picked
because the owner liked how the title looked on a machine that substituted
Liberation Mono for Courier New). It was removed with the font change below;
it's in git history if ever wanted.

`images/header-name1.jpg` / `header-name2.jpg` are the old header images and
are no longer used.

## Fonts

One font for all text (owner's choice, 2026-11-09, "simple text
throughout"): **Instrument Sans**, regular weight only, Latin subset, bundled
as `fonts/instrument-sans-latin-400-normal.woff2` (17 KB, from the
`@fontsource/instrument-sans` npm package; SIL Open Font License in
`fonts/instrument-sans-OFL.txt`). Set once on `body`, so sidebar links,
photo captions, Super 8 titles/dates/paragraphs and the "coming soon" line
all inherit it; fallbacks are Helvetica Neue, Arial, sans-serif. It was
picked over Inter, Arimo, DM Sans, Work Sans and Geist partly because it's
narrow, so phone captions with a place ("Fall 2025 · Seattle, WA") fit on
one line more often. The sidebar links alone use **semibold (600)**,
`fonts/instrument-sans-latin-600-normal.woff2` (17 KB, same package):
outlined cream letters need thicker strokes for the cream to show (regular
looked thin; bold looked heavy next to the title). Nothing else uses bold
or italic; if that changes, add the matching file from the same package
rather than letting the browser fake it.
No preload: hidden captions and sidebar links still lay out text, so the
font is fetched early anyway.

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

**Opening the menu slides the page down** (owner's request, 2026-11-09), so
the links sit on the mountains instead of on the first photo (dark-gray
link text over a dark photo was unreadable). `toggleSidebar()` sets
`--menu-space` to 24px below the last link (measured each time, so new
links are accounted for) and adds `body.menu-push`, which raises the Film
and Super 8 pages' top padding from 100px to that, animated with the
slide. Only when opened within 100px of the top; further down, sliding
would just make the photos on screen jump, so the links sit over photos
there. The owner explicitly does **not** want a backdrop or a strip of
the mountain picture behind the links ("I want it to be clear").

Pages are `<main>` sections in `index.html`, switched by the URL hash in
`showCurrentPage()`: `#super8` shows Super 8; anything else (no hash, `#`,
`#film`, the old `#photography`, typos) shows Film. The title also goes home
(see Logos).

## Film page (photo gallery)

Lives inside `index.html` as `<main id="film">`, shown at the bare address
and at `#film` (see Sidebar). No separate HTML page, so the header and
sidebar aren't duplicated.

- Photo list: `photos.js` (`window.PHOTOS`), displayed in file order. Each
  entry is `{ src, season, year, location?, poster? }`. `src` is a repo path
  under `images/photography/` or a full `https://` URL from an image host.
  A `src` ending in `.mp4` is a clip (see below) and `poster` is its still.
- **Drive is the source of truth** (owner's workflow since 2026-11-09). The
  owner arranges the Film Photos folder and Claude mirrors it with
  `tools/sync_film.py` (usage in the file): fetch the folder listing with
  the Drive connector, dry-run, then `--apply`, test, push. It mirrors:
  - **Order** — by file name as text, newest first. In-between numbers slot
    a file in (00211 between 00210 and 00230; 006001 after 00600).
  - **Place and camera** — `00010 Ann Arbor, MI (Pentax K1000).jpg` →
    "Fall 2025 · Ann Arbor, MI · Pentax K1000" (`location` and `camera` in
    photos.js). Both optional; nothing after the number, or the camera's own
    file name, means neither, and the caption is just season and year
    (owner chose "date + place" over place-only). Non-photo files in the
    folder (e.g. an example-name doc) are ignored.
  - **Removals** — files moved out of the folder come off the site.
  - **Renumbering** — site files are renamed to the Drive number, so
    `00450.jpg` here is always `00450 …` there.
  `tools/film-drive-files.json` links each site file to its Drive file ID
  and original camera name (so renamed files are still recognised). The
  script refuses to run if photos.js has entries with no link. New Drive
  files are only reported; add them by hand (processing below), add their
  links, and re-run.
- **Bulk rename done (2026-11-09).** Every Drive file was renamed to its
  number, renumbered by tens in the owner's order (`00010` … `02240`), plus a
  guessed place where Claude could tell: Berlin (1), Nepal (19), Japan (20),
  Michigan (6) — the four places the owner named. The other 178 (Seattle?,
  Hawaii, Glacier, Chicago, Colorado, Yellowstone, Sedona, Montreal,
  Savannah by the look of them) were left with just a number for the owner's
  pass-over. **Owner's pass-over, in progress:** so far 00010 Washington,
  00020–00040 Seattle, 00440 Michigan (Japan was wrong for it),
  00450–00940 Hawaii, 00960–00993 Michigan (01010 moved to `00993` to join
  them), 00994–01002 LA (00990, 00950 and 01040/01050 moved to `00994`,
  `00995` and `01001`/`01002` to join that group), 01060–01130 Colorado
  (spring 2021 trip) and 01681–01910 Colorado (a separate summer 2020
  trip around Lake Dillon; 01440–01520 moved to `01681`–`01689` to join
  it, along with 01670–01680, the same Lake Dillon night view),
  01140–01340 Montana, 01380 North Dakota (bison; the owner's guess at the
  badlands, could be South Dakota), 01400–01430 Chicago, 01530–01580
  Grand Tetons, 01590–01660 Yellowstone (the owner said "tetons"; the
  geysers and hot springs are Yellowstone, so Claude split them),
  01920–02020 Sedona, AZ (the owner first said Colorado for 01690–01930;
  asked, 01920–01930 were Sedona), 02030–02120 Toronto, 02190–02210 North
  Carolina (not Savannah). Places the owner doesn't know are "USA":
  01350–01370, 01390, 02130, 02230–02240. **Every photo now has a place**
  (2026-11-09).
- **Keep trips together** (owner's request, 2026-11-09). The order came
  from when rolls were developed, so one trip can be split across rolls.
  When the same place shows up in two runs from about the same time,
  rename the smaller run in Drive with in-between numbers so it sits next
  to the larger run (on the side it came from), then sync. Done so far:
  Colorado 01020/01030 → `01083`/`01086` and 01440–01520 →
  `01681`–`01689`, Michigan 02220 → `02185` and 01010 → `00993`, LA 00990
  → `00994`. Same
  place a year or so apart is a different trip; leave it. A Google Doc named `00000 Michigan (Pentax K1000)` at the top
  of the folder shows the format and explains it; the sync script ignores
  non-photo files. The original camera file names are kept in
  `tools/film-drive-files.json` (`original`).
- Current contents: 195 film photos and 29 RETO "3D" clips (imported
  2026-11-06 as 231 photos + 29 clips; the owner has since moved 36 stills
  out of Film Photos, 29 of them into "Reto Image Stills").
- Site copies are made from the Drive originals: EXIF rotation baked in
  (00780–00810 were stored sideways with a rotate flag), long edge 1600px,
  progressive JPEG quality 80, metadata stripped (~330 KB each) **except
  the colour profile**: some 3D-camera stills are Display P3 (29 were; 6
  remain on the site: 00290, 00450, 00510, 00550, 00630, 00720) and must
  keep their ICC profile, or browsers read them as sRGB and they look ~13%
  less saturated (fixed 2026-11-09; they had been stripped). Files
  without a profile, or with plain sRGB, need nothing. Clips are
  silent H.264 MP4 (CRF 23, `+faststart`, ~400 KB) with a first-frame poster
  JPEG of the same number.
- Captions: season + year from each photo's Google Takeout date (read in
  Ann Arbor time; for some scans that may be the upload date, so the owner
  may ask for corrections), plus the place from the Drive file name.
  Dates aren't in the Drive names: correct them by editing `season`/`year`
  in photos.js, and the sync keeps the edit. Corrected so far: 00450 and
  00460 Spring 2024 → Summer 2021 (Hawaii, re-uploaded later). The
  "Film captions" Google Sheet from 2026-11-06 is superseded by the Drive
  names.
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
  `NNNNN original-name` (5 digits, newest first, counting by tens).
  Photos and clips only, one file per photo.
- **Film Photos – Takeout data** — the Takeout `.supplemental-metadata.json`
  files (dates, etc.) moved out of the way.
- **Reto Image Stills** — RETO 3D stills the owner took off the site
  (2026-11-09). Anything moved out of Film Photos should come off the site.
- All 41 originals that had an `-edited` copy were moved to the Drive trash
  (2026-11-09, owner's request: no duplicates), so Film Photos holds one
  file per photo: the `-edited` one where it exists (which the site already
  used). 14 were only un-rotated versions; 27 also lacked Google Photos
  colour/crop edits. The owner may rename files while re-sorting (e.g.
  `006001 RETO-…mp4`, formerly 00070), so match by Drive file ID, not name.
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
