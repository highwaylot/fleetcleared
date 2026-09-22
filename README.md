# FleetCleared — design preview

Static site, no build step. Open `index.html` in a browser, or serve the folder with any static host.

**Preview mode is on.** Every page has `<meta name="robots" content="noindex, nofollow">` and `robots.txt` blocks all crawlers, so nothing gets indexed by search engines.

## Files

| Path | What it is |
|---|---|
| `index.html` | Home |
| `browse.html` | Find a consultant (sample listings live in `assets/site.js`) |
| `for-consultants.html` | Consultant signup |
| `privacy.html`, `terms.html` | Legal drafts: fill the highlighted placeholders and get a lawyer's review |
| `admin.html` | Admin mockup. Not linked from any public page |
| `assets/site.css`, `assets/site.js` | Shared styles and behavior |
| `favicon.ico`, `favicon.svg`, `assets/icons/`, `site.webmanifest` | Browser, iOS and Android icons |
| `assets/og-image.png` | Link preview image for Facebook, texts, etc. |
| `sitemap.xml`, `robots.txt` | Search engine files |

## Before going live

1. **Admin needs real sign-in.** Hiding the page is not security. Put `admin.html` behind authentication (for example Supabase Auth or Vercel password protection) or move it into the real app.
2. **Legal pages:** fill every highlighted placeholder, have a lawyer review them, then delete the "Draft for review" note.
3. **Create inboxes** for `privacy@fleetcleared.com` and `legal@fleetcleared.com`.
4. **Turn on indexing:** in every public page change `noindex, nofollow` to `index, follow` (leave `admin.html` as noindex), and replace `robots.txt` with:
   ```
   User-agent: *
   Disallow: /admin.html
   Sitemap: https://fleetcleared.com/sitemap.xml
   ```
5. **Google Search Console:** verify `fleetcleared.com` with a DNS TXT record (no code change needed), then submit `sitemap.xml`.
6. **Forms:** the contact and signup forms only show a confirmation right now. Wire them to the backend so each contact request is stored as a lead.
