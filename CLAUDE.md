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
resolves to the IPs above. Then check **Settings -> Pages -> Enforce HTTPS**
in the repo so `http://` redirects to `https://`. If that checkbox is greyed
out, the cert hasn't been issued yet — remove and re-add the custom domain in
Pages settings to retrigger provisioning, then wait (can take up to 24h).

## Gotchas

- Keep all page assets on relative or `https://` URLs. Any `http://` asset
  triggers a mixed-content warning even when the page itself is served over
  HTTPS. (Currently clean.)
