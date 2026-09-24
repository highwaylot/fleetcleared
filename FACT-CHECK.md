# Fact-check before the public launch

Every checkable claim in the guides, with where to confirm it. Open the source, confirm the claim still holds, and tick the box.
If anything differs, tell Claude (or edit `tools/build_guides.py`) and rebuild. Re-check this list every January.

FMCSA and eCFR pages were blocked from Claude's workspace, so none of these were confirmed against the primary source.

## New entrant safety audit
- [ ] New carriers are in an 18-month monitoring period and audited within the first 12 months (passenger carriers: 120 days). Source: eCFR Part 385 Subpart D
- [ ] Audits can be on-site or off-site. Source: FMCSA New Entrant help center
- [ ] 2022: 63,672 audits, 92.2% pass. 2023: 58,600 audits, 91.3% pass. Source: industry reports; find FMCSA's own figure or drop the numbers
- [ ] An accident register is required even if empty (49 CFR 390.15)
- [ ] Ignoring the audit notice can be treated as a failure

## The 16 automatic-fail violations
- [ ] The list of 16 and their section numbers match 49 CFR 385.321(b) exactly
- [ ] Only 395.8(a) and 396.17(a) need 51% or more of records; the other 14 fail on one instance
- [ ] General freight minimum insurance is usually $750,000 (49 CFR 387.9)
- [ ] The "most common" order: we say FMCSA doesn't publish per-rule counts. Search once more for an FMCSA count

## Failed audit
- [ ] Corrective action plan within 15 days of the notice. Source: FMCSA CAP guidance PDF
- [ ] 60 days for property carriers, 45 for passenger and placarded hazmat carriers; revocation on day 61 / 46. Source: 49 CFR 385.319(c), 385.325
- [ ] Administrative review of a failed audit is available (49 CFR 385.329) and the notice explains how

## Drug and alcohol
- [ ] Part 382 covers CDL vehicles: 26,001+ lb, 16+ passengers including driver, or placarded hazmat
- [ ] Owner-operators must be in a consortium random pool (49 CFR 382.103 / 382.305)
- [ ] 2026 random testing rates: 50% drug, 10% alcohol. Source: FMCSA Federal Register notice for calendar year 2026

## Clearinghouse
- [ ] Full query before hire; limited query at least every 12 months (49 CFR 382.701)
- [ ] Full query within 24 hours after a limited query shows information
- [ ] Limited-query consent can be a multi-year written consent
- [ ] Owner-operators must designate a C/TPA

## CSA warning letters
- [ ] Thresholds: Unsafe Driving, HOS, Crash 65 / 60 hazmat / 50 passenger; Vehicle Maintenance, Controlled Substances, Driver Fitness 80 / 75 / 65; HM Compliance 80. Source: FMCSA SMS methodology
- [ ] No written reply to a warning letter is required. Source: OOIDA tip sheet / FMCSA
- [ ] SMS updates monthly

## Deadlines and MCS-150
- [ ] MCS-150 schedule: last digit = month (0 = October), next-to-last digit odd/even = year (49 CFR 390.19)
- [ ] Penalty up to $1,000/day, $10,000 cap (inflation adjusted), and deactivation for missing it
- [ ] Current status of FMCSA's Motus transition and any paused enforcement
- [ ] Filing the MCS-150 with FMCSA is free
- [ ] IFTA due Jan 31, Apr 30, Jul 31, Oct 31. Form 2290 due Aug 31, tax year Jul 1 – Jun 30. UCR opens Oct 1, due Dec 31
- [ ] 2026 Roadcheck May 12–14; Brake Safety Week Aug 23–29 (update to 2027 dates when CVSA announces them)
