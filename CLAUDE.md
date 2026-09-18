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

Status as of 2026-09-18: GitHub Pages reports **"DNS check successful"**, so the
A records below are correct and GoDaddy forwarding is NOT in play. The open
problem is certificate issuance (see HTTPS below).

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

**Open issue:** as of 2026-09-18 that checkbox reads "Unavailable for your site
because a certificate has not yet been issued" — despite the DNS check passing
and the `CNAME` file having been in place since 2025-03-12. An 18-month stall
is not normal provisioning latency; something is blocking issuance.

Fixes, in order:

1. Remove the custom domain in Pages settings, save, re-add it, save. This is
   the only way to retrigger a provisioning job that failed earlier — GitHub
   does not retry on its own. Note this deletes and recreates the repo's
   `CNAME` file as real commits on `main`, so `git pull` afterwards.
2. Check for a **CAA record** on the apex. If one exists and does not authorize
   `letsencrypt.org`, issuance fails permanently and silently. Delete it or add
   `letsencrypt.org`.
3. Check for **AAAA records** on the apex. Pages has no IPv6 there, but Let's
   Encrypt prefers IPv6 when an AAAA exists, so a stale one breaks domain
   validation while GitHub's DNS check (A records only) still passes. Delete
   any AAAA on the apex.

## Gotchas

- Keep all page assets on relative or `https://` URLs. Any `http://` asset
  triggers a mixed-content warning even when the page itself is served over
  HTTPS. (Currently clean.)
