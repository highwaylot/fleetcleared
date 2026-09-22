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
| `assets/rules.js` | **Business rules: lead pricing and signup screening.** Every number lives at the top of this file |
| `assets/admin.js` | Admin preview. Scores, reasons and charges come from `rules.js` |
| `application-status.html` | What a flagged applicant sees, with the "Ask for a second look" form. Reached from the review email, not the menu |
| `demo/` | **Taste of FleetCleared**: a copy of the site with fictional example consultants (top rated, low rated, brand new, monthly limit reached, flagged application) to show prospective consultants. Data lives in `assets/demo-data.js`, which only the demo loads. The live pages start with no listings |
| `tests/` | Automated checks for the business rules. Run `npm test` |
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

## Pricing and screening rules

Both live in `assets/rules.js`, so the site, the admin page and the tests use the same code.

**Lead price** comes from the carrier's fleet size: 1–2 trucks $30, 3–10 trucks $45, 11+ trucks $65. For each request, `decideLead` decides, in this order:
1. The business hasn't used its free lead yet: deliver it free.
2. The consultant has hit their monthly limit: decline and tell the carrier. No charge.
3. No card on file: hold for up to 48 hours. No charge.
4. Otherwise: deliver and charge the tier price.

`suggestedPrice` is the re-pricing formula for later (close rate × first-year client value × our cut), kept between $25 and $90.

**Screening** adds points for warning signs (same phone as another account +60, free email +10, and so on) and subtracts points for good signs. The total picks a band:
- **Clear** (0–24): quick look, then approve.
- **Check** (25–59): read the reasons first.
- **Hold** (60+): contact the applicant before deciding.

It never rejects anyone automatically. A lookup that hasn't run (for example the state registry) adds no points, so missing data never counts against an applicant. Accounts that share a phone, address, card or company email domain count as one business and share one free lead.

**Changing a number:** edit it in `rules.js`, update the matching test in `tests/rules.test.js`, and run `npm test`. If you change a lead price, also update the prices in the terms of service. A test fails until you do.
