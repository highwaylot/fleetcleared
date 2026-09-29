# FleetCleared

Free-to-list directory connecting small trucking companies (1-20 trucks) with
DOT/FMCSA compliance consultants. Carriers: always free. Consultants: one free
lead per business, then card on file, auto-charged by fleet size at delivery
($30 for 1-2 trucks, $45 for 3-10, $65 for 11+). Directory only — never
certifies, vouches for, or gives compliance advice. Verification of consultant
info (entity name, contact, basic reputation) is for FleetCleared's own
confidence, not a claim to carriers that a listee is "good" — never phrase
copy or drafts in a way that reads as endorsement.

Live at fleetcleared.com (Vercel). Repo `highwaylot/fleetcleared`. Work on
`claude/new-session-dkn70h`, fast-forward merged into `main` to deploy.

Owner is a solo, non-technical founder (veteran, pursuing a TX veteran-owned
LLC fee waiver via TVC). Treat this as a real small business, not a coding
exercise — grounded, no hype, no cheerleading.

## Drafting outreach emails/messages for the owner to send

- Write them **short**. Default to 4-6 sentences. Cut anything that isn't a
  question, an ask, or information the recipient needs to act.
- **Do not re-explain or re-justify a decision once the owner has made it.**
  If they say "no" to something (e.g. don't list X, don't offer Y), the draft
  states the decision plainly and moves on — no paragraph defending it, no
  restating the reasoning back to them, no hedging language like "just to be
  clear" or "mainly because."
- **Do not invent or repeat pleasantries not asked for** ("glad that worked
  out," "great resource," "no worries at all") — they read as filler and the
  owner has called this out as fake-sounding more than once. If a line isn't
  load-bearing, drop it.
- When the owner corrects a draft, apply the correction fully on the next
  pass — don't let rejected phrasing resurface in a later revision of the
  same draft.
- Default style: plain, direct, a little informal. Not corporate, not
  apologetic, not over-explained.
- Drafts go in the chat reply for the owner to copy/paste and send manually —
  do not create or edit Gmail drafts via tool unless explicitly asked to.

## Engineering conventions

- `api/*.py`: zero-dependency, stdlib-only (no `requirements.txt`). External
  services (Stripe, Resend, Vercel KV) via raw `urllib.request`, never SDKs.
- `assets/rules.js` is the pricing/decision spec; `api/_rules.py` is a
  hand-kept parity port, checked against `tests/rules.test.js` via its own
  `__main__` self-test block. Keep both in sync by hand if either changes.
- Run `npm test` after touching pricing/lead-decision logic.
