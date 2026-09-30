# FleetCleared — design preview

Static site. Open `index.html` in a browser, or serve the folder with any static host.

**Pages are generated.** Edit `tools/build_site.py` (site pages) or `tools/build_guides.py` (guides and free tools), then run `python3 tools/build_site.py`. Don't hand-edit the generated `.html` files; the next build overwrites them.

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
| `assets/hours.js` | Works out "Open now" / "Closed · opens tomorrow at 7:00 AM" in the consultant's own time zone. Tested in `tests/hours.test.js` |
| `assets/admin.js` | Admin preview. Scores, reasons and charges come from `rules.js` |
| `application-status.html` | What a flagged applicant sees, with the "Ask for a second look" form. Reached from the review email, not the menu |
| `demo/` | **Taste of FleetCleared**: a copy of the site with fictional example consultants (top rated, low rated, brand new, monthly limit reached, flagged application) to show prospective consultants. Data lives in `assets/demo-data.js`, which only the demo loads. The live pages start with no listings |
| `review.html` | **Founder review hub**: links to every live page, every demo example, and a log of each saved version. Not linked anywhere, never indexed. Remove or put behind sign-in before launch |
| `guides.html`, `guide-*.html` | **Guides**: plain-language answers for carriers (safety audit, drug and alcohol, CSA letters, deadlines). Each shows "Waiting for review by a listed consultant" until one reviews it |
| `mcs-150-due-date.html`, `audit-readiness-check.html` | **Free tools.** Math lives in `assets/deadlines.js` (tested); page behavior in `assets/guides.js`. Nothing entered is saved or sent |
| `tools/` | The page generator (`build_site.py`, `build_guides.py`) |
| `tests/` | Automated checks for the business rules, opening hours and deadline math. Run `npm test` |
| `favicon.ico`, `favicon.svg`, `assets/icons/`, `site.webmanifest` | Browser, iOS and Android icons |
| `assets/og-image.png` | Link preview image for Facebook, texts, etc. |
| `sitemap.xml`, `robots.txt` | Search engine files |

## Public soft launch (guides only)

Builds a separate, public version with just the home page, guides, free tools, terms and privacy. No directory, forms, admin, demo or review hub, and no fake confirmations:

1. Fill every field in `tools/launch.json` (company legal name, state, mailing address, courts, liability cap, effective date).
2. Work through `FACT-CHECK.md`.
3. Run `FC_LAUNCH=1 python3 tools/build_site.py`. It writes the site to `dist/` (not saved in git) and **refuses to finish** while any placeholder, noindex tag, draft note, directory link or reminder form remains.
4. **Hosting is Vercel**, connected to this repo. `vercel.json` tells it to run the launch build and serve `dist/`. Production updates when `main` changes. Right now `vercel.json` includes `FC_HOLD_INDEX=1`, which publishes the guides but keeps search engines out while the company details are blank. Delete `FC_HOLD_INDEX=1` from `vercel.json` once `tools/launch.json` is filled, and the next deploy is fully public and indexable.
5. Create the inboxes `legal@`, `privacy@`, `partnerships@` and `hello@fleetcleared.com` (catch-all for automated emails and anything that doesn't fit the other three).
6. In Google Search Console, verify the domain and submit `https://fleetcleared.com/sitemap.xml`.
9. **Waitlist:** self-hosted, no third party -- but Vercel retired its own KV product, so the Storage tab now routes through the Vercel Marketplace to Upstash (the same company that used to power Vercel KV underneath). Same result: free, forever, no credit card, plenty for a waitlist (500,000 commands a month).
   - Vercel project -> **Storage** tab -> **Marketplace Database Providers** (or **Browse Marketplace**, wording varies) -> search **Upstash** -> **Redis** -> pick the **Free** plan -> **Connect to Project**. That sets `KV_REST_API_URL` / `KV_REST_API_TOKEN` (or `UPSTASH_REDIS_REST_URL` / `_TOKEN` -- the code reads either name) automatically.
   - **Settings -> Environment Variables** -> add `ADMIN_SECRET` (any password you pick) for Production -> redeploy.
   - Carrier signups (home page) and consultant signups (`for-consultants.html`) land in separate lists via `api/waitlist.py`. Read them at `/waitlist-7f2c9a1d.html` (enter your `ADMIN_SECRET` once; the page remembers it, and has a tab for each list plus a "Copy all emails" button).
10. **When you're ready to actually email the list (2027):** send one message first asking people to confirm they still want to hear from you, and only continue mass-emailing whoever clicks. A list that's sat untouched for months looks like a cold list to spam filters otherwise; a single reconfirmation at send time fixes that without building a live double opt-in flow today.
7. In Vercel: Project -> Analytics -> Enable (free, cookieless page-view counts; already disclosed in the launch privacy policy).
8. Bookmark the private status page: `https://fleetcleared.com/status-3b3500e3.html`. It's not linked anywhere and is blocked from search, so this URL is the only way to reach it. Links to every public page plus Vercel Analytics and Search Console. To retire it, change `STATUS_SLUG` in `tools/build_launch.py` and rebuild; the old URL stops working.

## Consultant applications (real backend)

The signup form on `for-consultants.html` (the full preview build, not the guides-only launch site)
now submits for real:

- `api/consultant_apply.py` -- public, no auth. Validates the form, screens the applicant against
  every other application on file (same signals as `assets/rules.js` SCREENING: same phone, similar
  name, free email, government-style wording -- the ones that don't need a paid external lookup),
  and stores it in Vercel KV as `pending`.
- `api/admin_consultants.py` -- private, `?key=<ADMIN_SECRET>`. Lists applications by status and
  approves/rejects/second-looks them. Approving copies a trimmed record into a public-listings
  store.
- `api/consultants_public.py` -- public, no auth. Every approved listing. Not wired into
  `browse.html`/`consultant.html` yet -- those still read `window.FC_DEMO_CONSULTANTS` in the
  preview and aren't part of the public launch build at all. Wiring them up is a frontend-only
  follow-up now that the data exists.
- Admin panel: `/consultants-9d4e1f2a.html` (private, unguessable, noindex, linked from the status
  page). Enter your `ADMIN_SECRET` once; shows each application's screening score and reasons with
  Approve / Reject / Ask for a second look buttons.
- The Taste of FleetCleared demo (`demo/for-consultants.html`) never calls the real endpoint --
  `assets/site.js` checks for `window.FC_DEMO_CONSULTANTS` (set by `assets/demo-data.js`) and shows
  the same success message locally instead, so playing with the demo can't pollute real applications.

**Still not built, on purpose:** consultants can't log in to manage their own listing (editing or
pausing it requires asking you, for now). That's a separate, larger build. Email sending and
carrier-side lead requests/billing are covered in the next section.

The preview (plain `python3 tools/build_site.py`) is unchanged and stays noindex.

## Lead billing (real backend)

The "Request contact" button on `consultant.html` submits for real now, and it can actually charge
a consultant's card. Three moving pieces, in the order data flows through them:

1. **`api/lead_request.py`** -- public, no auth. A carrier's request lands here. Runs the pricing
   spec in `api/_rules.py` (a hand-kept port of `assets/rules.js`'s `decideLead` -- same numbers,
   same order of checks) to decide: deliver free, deliver and charge, hold (no card on file yet), or
   decline (consultant's monthly limit is reached). On a paid deliver it charges the consultant's
   saved card through Stripe; on hold or a declined charge it emails the consultant instead of
   handing over the carrier's contact details, so a lead is never given away before it's paid for
   (or confirmed free).
2. **`api/consultant_card_setup.py` + `add-card.html`** -- how a consultant adds a card. Stripe
   Elements collects the card directly in the browser; our server only ever sees a Stripe customer
   id and payment method id, never the card number. Linked from the approval email
   `api/admin_consultants.py` now sends.
3. **`api/stripe_webhook.py`** -- Stripe's confirmation that a card was actually saved
   (`setup_intent.succeeded`) is what gets written to the consultant's record, not the browser's
   side of the form. This is Stripe's own recommended pattern, not a shortcut.

A hold that never gets a card added expires after 48 hours (`api/cron_expire_holds.py`, wired up in
`vercel.json`'s `crons`), matching what `terms.html` already promises. It emails the carrier (when
they asked to be reached by email) that the consultant wasn't able to take the request.

**Setup, in order:**

1. **Stripe.** Create an account at [stripe.com](https://stripe.com) if you don't have one. Start
   in **test mode** (the toggle in the dashboard) -- everything above works identically in test mode
   with Stripe's [test card numbers](https://stripe.com/docs/testing), so you can run a whole fake
   lead through the system before any real card is charged.
   - **Developers -> API keys**: copy the **Secret key** (`sk_test_...`) and **Publishable key**
     (`pk_test_...`).
   - **Developers -> Webhooks -> Add endpoint**: URL `https://fleetcleared.com/api/stripe_webhook`,
     events `setup_intent.succeeded` and `payment_intent.payment_failed`. Copy the **Signing
     secret** (`whsec_...`) it gives you.
   - In Vercel, **Settings -> Environment Variables**, add `STRIPE_SECRET_KEY`,
     `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET` with those three values.
   - When you're ready to actually charge real cards: flip to **live mode** in Stripe, get the
     `sk_live_...`/`pk_live_...`/`whsec_...` equivalents (a live webhook endpoint is separate from
     the test one), and swap the env vars.
2. **Resend** (email sending -- lead notifications, approval emails, hold/decline notices). Create
   a free account at [resend.com](https://resend.com), verify `fleetcleared.com` as a sending domain
   (a few DNS records, same place you manage the domain's other DNS), then **API Keys -> Create**.
   Add `RESEND_API_KEY` and `RESEND_FROM` (e.g. `FleetCleared <hello@fleetcleared.com>`) in Vercel.
   Any email send silently no-ops until these are set -- nothing breaks, leads just stop notifying
   anyone, so don't skip this once real consultants are live.
3. **`CRON_SECRET`.** Any random string, added the same way. Vercel signs its own cron requests with
   it automatically once it's set; without it the cron endpoint runs unauthenticated (fine to leave
   unset while testing, not once this is live).
4. Redeploy after adding env vars -- Vercel doesn't pick up new ones on existing deployments.

**Testing it end to end**, once Stripe/Resend are in test mode: approve a test consultant
application, open the add-card link from the email it sends, add a Stripe test card
(`4242 4242 4242 4242`, any future expiry/CVC), then send that consultant a request from
`consultant.html` with a fleet size of 11+ so it's a paid lead, not the free one. You should get an
email with the lead's contact details and see the charge in Stripe's dashboard (test mode).

## Before going live

1. **Admin needs real sign-in.** Hiding the page is not security. Put `admin.html` behind authentication (for example Supabase Auth or Vercel password protection) or move it into the real app.
2. **Legal pages:** fill every highlighted placeholder, have a lawyer review them, then delete the "Draft for review" note.
3. **Create inboxes** for `privacy@fleetcleared.com`, `legal@fleetcleared.com`, `partnerships@fleetcleared.com` and `hello@fleetcleared.com`. Copyright notices and content corrections route to `legal@` -- no separate inboxes for those.
4. **Turn on indexing:** in every public page change `noindex, nofollow` to `index, follow` (leave `admin.html` as noindex), and replace `robots.txt` with:
   ```
   User-agent: *
   Disallow: /admin.html
   Disallow: /review.html
   Sitemap: https://fleetcleared.com/sitemap.xml
   ```
5. **Google Search Console:** verify `fleetcleared.com` with a DNS TXT record (no code change needed), then submit `sitemap.xml`.
6. **Forms:** the contact, signup and deadline-reminder forms only show a confirmation right now. Wire them to the backend so each contact request is stored as a lead and each reminder signup is stored with its consent.
7. **Guides:** have a listed consultant review each guide, then replace "Waiting for review" with their name. Get a short written reviewer agreement first (they checked it for accuracy, it isn't their advice to readers, no pay or ranking boost for reviewing). Re-check every date and figure against the linked sources, and ask the lawyer to review the "Guides, free tools and reminders" section of the terms.

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

The government check looks for government words in the business name, but in the description only flags claims to be or act for the government ("official FMCSA", "on behalf of the DOT"), so "former FMCSA investigator" isn't penalized.

It never rejects anyone automatically. A lookup that hasn't run (for example the state registry) adds no points, so missing data never counts against an applicant. Accounts that share a phone, address, card or company email domain count as one business and share one free lead.

**Changing a number:** edit it in `rules.js`, update the matching test in `tests/rules.test.js`, and run `npm test`. If you change a lead price, also update the prices in the terms of service. A test fails until you do.
