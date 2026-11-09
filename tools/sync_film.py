"""Bring the Film page in line with Nathan's Drive folder "Film Photos".

Nathan manages the gallery by renaming files in Drive:
  - order:     files are listed by name, so the number at the start sets the
               order (in-between numbers like 00211 or 006001 slot a file in
               between two others; names are compared as text, not values)
  - place:     whatever follows the number is the caption's place, e.g.
               "00010 Ann Arbor, MI.jpg" -> "Fall 2025 · Ann Arbor, MI".
               If nothing follows, or it's still the camera's own file name
               ("00010 AA011A-edited.jpg"), the photo has no place and the
               caption is just the season and year.
  - removal:   files moved out of the folder come off the site.

The site can't read the private Drive itself, so Claude fetches a listing of
the folder with the Google Drive connector (search_files with
"parentId = '<Film Photos id>' and trashed = false", saved as JSON:
{"files": [{"id", "title", "mimeType"}, ...]}) and runs:

    python3 tools/sync_film.py LISTING.json            # show what would change
    python3 tools/sync_film.py LISTING.json --apply    # change photos.js and files

It keeps tools/film-drive-files.json (site file name -> Drive file ID and
the file's original camera name), so a photo is recognised even after Nathan
renumbers or renames it. New Drive files aren't on the site yet: they're
listed so Claude can download and add them (long edge 1600px, JPEG q80,
keep any colour profile; clips as silent H.264 with a poster), then add
them to film-drive-files.json and run this again.
"""
import json, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP = os.path.join(REPO, 'tools', 'film-drive-files.json')
PHOTOS = os.path.join(REPO, 'photos.js')
IMG = 'images/photography'
EXT = re.compile(r'\.(jpe?g|png|heic|mp4|mov)$', re.I)


def js(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"


def parse_photos():
    src = open(PHOTOS, encoding='utf-8').read()
    head, body = src.split('window.PHOTOS = [', 1)
    entries = {}
    for line in body.split('\n'):
        m = re.search(r"src: '" + IMG + r"/([^.']+)\.(jpg|mp4)'", line)
        if not m:
            continue
        e = {'name': m.group(1), 'ext': m.group(2)}
        for key in ('season', 'location'):
            k = re.search(key + r": '((?:[^'\\]|\\.)*)'", line)
            if k:
                e[key] = k.group(1).replace("\\'", "'").replace('\\\\', '\\')
        y = re.search(r'year: (\d+)', line)
        if y:
            e['year'] = int(y.group(1))
        entries[e['name']] = e
    return head, entries


def entry_line(e):
    parts = [f"src: '{IMG}/{e['name']}.{e['ext']}'"]
    if e['ext'] == 'mp4':
        parts.append(f"poster: '{IMG}/{e['name']}.jpg'")
    if 'season' in e:
        parts.append(f"season: {js(e['season'])}")
    if 'year' in e:
        parts.append(f"year: {e['year']}")
    if e.get('location'):
        parts.append(f"location: {js(e['location'])}")
    return '    { ' + ', '.join(parts) + ' },'


def main():
    listing = json.load(open(sys.argv[1], encoding='utf-8'))['files']
    apply = '--apply' in sys.argv
    links = json.load(open(MAP, encoding='utf-8'))
    by_id = {l['drive_id']: l for l in links}
    head, entries = parse_photos()
    unlinked = sorted(set(entries) - {l['site'] for l in links})
    if unlinked:
        sys.exit('photos.js has entries with no Drive link (add them to '
                 'film-drive-files.json first, or they would be dropped): '
                 + ', '.join(unlinked))

    drive = sorted(listing, key=lambda f: f['title'].split(' ', 1)[0])
    new_files = [f['title'] for f in drive if f['id'] not in by_id]
    listed_ids = {f['id'] for f in drive}
    removed = [l for l in links if l['drive_id'] not in listed_ids]

    order, renames, places = [], [], []
    for f in drive:
        link = by_id.get(f['id'])
        if not link:
            continue
        prefix, _, rest = f['title'].partition(' ')
        rest = EXT.sub('', rest.strip()).strip()
        place = '' if rest.lower() in ('', link['original'].lower()) else rest
        e = entries[link['site']]
        if prefix != link['site']:
            renames.append((link['site'], prefix))
        if (e.get('location') or '') != place:
            places.append((prefix, e.get('location') or '', place))
        order.append((link, prefix, place))

    old_order = [l['site'] for l in links if l['drive_id'] in listed_ids]
    moved = [p for (l, p, _), o in zip(order, old_order) if l['site'] != o]
    print(f'{len(order)} on the site after sync; {len(new_files)} new in Drive; '
          f'{len(removed)} removed; {len(renames)} renumbered; '
          f'{len(places)} place changes; order changed: {bool(moved)}')
    for t in new_files:
        print('  NEW (needs adding):', t)
    for l in removed:
        print('  remove:', l['site'], l['original'])
    for a, b in renames:
        print(f'  renumber: {a} -> {b}')
    for p, a, b in places:
        print(f'  place {p}: {a or "(none)"} -> {b or "(none)"}')
    if not apply:
        print('(dry run; add --apply to make these changes)')
        return

    git = lambda *a: subprocess.run(['git', '-C', REPO, *a], check=True)
    for l in removed:
        e = entries.pop(l['site'])
        for ext in {e['ext'], 'jpg'}:
            p = f"{IMG}/{l['site']}.{ext}"
            if os.path.exists(os.path.join(REPO, p)):
                git('rm', '-q', p)
    # Rename in two steps (via a temporary name) so swapped numbers don't collide
    for a, _ in renames:
        for ext in ('jpg', 'mp4'):
            if os.path.exists(os.path.join(REPO, IMG, f'{a}.{ext}')):
                git('mv', f'{IMG}/{a}.{ext}', f'{IMG}/{a}.sync-tmp.{ext}')
    for a, b in renames:
        for ext in ('jpg', 'mp4'):
            if os.path.exists(os.path.join(REPO, IMG, f'{a}.sync-tmp.{ext}')):
                git('mv', f'{IMG}/{a}.sync-tmp.{ext}', f'{IMG}/{b}.{ext}')
    lines, new_links = [], []
    for link, prefix, place in order:
        e = dict(entries[link['site']], name=prefix)
        if place:
            e['location'] = place
        else:
            e.pop('location', None)
        lines.append(entry_line(e))
        new_links.append(dict(link, site=prefix))
    open(PHOTOS, 'w', encoding='utf-8').write(head + 'window.PHOTOS = [\n' + '\n'.join(lines) + '\n];\n')
    open(MAP, 'w', encoding='utf-8').write(
        '[\n' + ',\n'.join('  ' + json.dumps(l, ensure_ascii=False) for l in new_links) + '\n]\n')
    print('applied')


if __name__ == '__main__':
    main()
