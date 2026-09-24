const test = require('node:test');
const assert = require('node:assert/strict');
const R = require('../assets/rules.js');

test('lead price follows fleet-size tiers, including the edges', () => {
  assert.equal(R.leadPrice(1), 30);
  assert.equal(R.leadPrice(2), 30);
  assert.equal(R.leadPrice(3), 45);
  assert.equal(R.leadPrice(10), 45);
  assert.equal(R.leadPrice(11), 65);
  assert.equal(R.leadPrice(400), 65);
});

test('fleet size must be a whole number of at least 1', () => {
  for (const bad of [0, -3, 2.5, 'abc', null]) assert.throws(() => R.leadPrice(bad));
});

test('first lead for a business is free, even without a card', () => {
  const d = R.decideLead({ freeLeadUsedByBusiness: false, cardOnFile: false, leadsThisMonth: 0, monthlyCap: null }, 12);
  assert.deepEqual([d.action, d.charge], ['deliver', 0]);
});

test('after the free lead: no card means hold, never a silent charge', () => {
  const d = R.decideLead({ freeLeadUsedByBusiness: true, cardOnFile: false, leadsThisMonth: 0, monthlyCap: null }, 5);
  assert.deepEqual([d.action, d.charge], ['hold', 0]);
});

test('after the free lead with a card: charged the tier price', () => {
  const d = R.decideLead({ freeLeadUsedByBusiness: true, cardOnFile: true, leadsThisMonth: 3, monthlyCap: 10 }, 5);
  assert.deepEqual([d.action, d.charge], ['deliver', 45]);
});

test('monthly cap stops leads before any charge', () => {
  const d = R.decideLead({ freeLeadUsedByBusiness: true, cardOnFile: true, leadsThisMonth: 10, monthlyCap: 10 }, 5);
  assert.deepEqual([d.action, d.charge], ['decline', 0]);
});

test('suggested re-price stays between floor and ceiling', () => {
  assert.equal(R.suggestedPrice({ closeRate: 0.25, clientValue: 1500, cut: 0.1 }), 38);
  assert.equal(R.suggestedPrice({ closeRate: 0.05, clientValue: 500, cut: 0.1 }), 25);
  assert.equal(R.suggestedPrice({ closeRate: 0.9, clientValue: 20000, cut: 0.2 }), 90);
  assert.throws(() => R.suggestedPrice({ closeRate: 'x', clientValue: 1, cut: 1 }));
});

const existing = [
  { name: 'Midwest DOT Advisors LLC', phone: '(614) 555-0100', address: '100 North High Street, Columbus OH', email: 'ops@midwestdot.com', ip: '10.0.0.5', signedUpAt: '2026-09-01', cardFingerprint: 'card_A', freeLeadUsed: true },
  { name: 'Lone Star Compliance Group', phone: '210-555-0199', address: '9 Alamo Rd, San Antonio TX', email: 'hi@lonestarcg.com', ip: '10.0.0.9', signedUpAt: '2026-06-01', cardFingerprint: 'card_B', freeLeadUsed: false },
];

test('a clean, established applicant scores Clear', () => {
  const r = R.screen({ name: 'Great Plains Carrier Services', phone: '316-555-0142', address: '5 Main St, Wichita KS', email: 'team@greatplainscs.com', website: 'https://www.greatplainscs.com', inStateRegistry: true, associationMember: true, ip: '10.9.9.9', signedUpAt: '2026-09-20' }, existing);
  assert.equal(r.band, 'clear');
  assert.equal(r.score, 0, 'negative points never push the score below zero');
  assert.equal(r.freeLeadAlreadyUsed, false);
});

test('same phone written differently is still caught, and names the matching account', () => {
  const r = R.screen({ name: 'MDA Safety', phone: '614.555.0100', email: 'x@mdasafety.com' }, existing);
  assert.equal(r.band, 'hold');
  assert.ok(r.reasons.some((h) => h.key === 'samePhone' && h.reason.includes('Midwest DOT Advisors LLC')));
  assert.equal(r.freeLeadAlreadyUsed, true, 'shares a phone with a business that used its free lead');
});

test('address matches through common abbreviations', () => {
  const r = R.screen({ name: 'New Co', address: '100 N. High St., Columbus OH' }, existing);
  assert.ok(r.reasons.some((h) => h.key === 'sameAddress'));
});

test('near-identical company name is flagged; different names are not', () => {
  assert.ok(R.screen({ name: 'Midwest D.O.T. Advisors' }, existing).reasons.some((h) => h.key === 'similarName'));
  assert.ok(!R.screen({ name: 'Southeast Fleet Safety' }, existing).reasons.some((h) => h.key === 'similarName'));
});

test('free email alone lands in Clear, never Hold', () => {
  const r = R.screen({ name: 'Solo Safety Consulting', email: 'solo@gmail.com' }, existing);
  assert.equal(r.score, 10);
  assert.equal(r.band, 'clear');
});

test('shared internet address only counts within 30 days', () => {
  const recent = R.screen({ name: 'A', ip: '10.0.0.5', signedUpAt: '2026-09-20' }, existing);
  const old = R.screen({ name: 'B', ip: '10.0.0.9', signedUpAt: '2026-09-20' }, existing);
  assert.ok(recent.reasons.some((h) => h.key === 'sameRecentIp'));
  assert.ok(!old.reasons.some((h) => h.key === 'sameRecentIp'));
});

test('lookups that were not run add no points', () => {
  const r = R.screen({ name: 'Unknown Co', email: 'a@unknownco.com' }, []);
  assert.equal(r.score, 0);
});

test('band edges: 24 is Clear, 25 is Check, 60 is Hold', () => {
  const band = (score) => R.SCREENING.bands.find((b) => score <= b.max).key;
  assert.equal(band(24), 'clear');
  assert.equal(band(25), 'check');
  assert.equal(band(59), 'check');
  assert.equal(band(60), 'hold');
});

test('free lead is shared across one business, but a shared Gmail domain does not link strangers', () => {
  assert.ok(R.sameBusiness({ email: 'a@midwestdot.com' }, existing[0]));
  assert.ok(!R.sameBusiness({ email: 'a@gmail.com' }, { email: 'b@gmail.com' }));
  assert.ok(R.sameBusiness({ cardFingerprint: 'card_A' }, existing[0]));
});

test('terms of service quote the same lead prices as the pricing rules', () => {
  const fs = require('node:fs');
  const path = require('node:path');
  const terms = fs.readFileSync(path.join(__dirname, '..', 'terms.html'), 'utf8');
  for (const tier of R.PRICING.tiers) {
    assert.ok(terms.includes(`$${tier.price}`), `terms.html is missing the ${tier.label} price $${tier.price}`);
  }
});

test('many weak signals can reach Hold, but are never described as a duplicate', () => {
  const r = R.screen({ name: 'Quick DOT Help', email: 'q@yahoo.com', inStateRegistry: false, phoneLineType: 'voip', webPresenceFound: false, emailDomainAgeDays: 20 }, existing);
  assert.equal(r.band, 'hold');
  assert.ok(!r.reasons.some((h) => /same|matches/i.test(h.reason)), 'no match reasons when nothing matched');
});

test('names that sound like a government agency are flagged, ordinary "DOT" names are not', () => {
  assert.ok(R.screen({ name: 'USDOT Registration Center' }, []).reasons.some((h) => h.key === 'governmentStyle'));
  assert.ok(R.screen({ name: 'Acme', description: 'Official FMCSA filing service' }, []).reasons.some((h) => h.key === 'governmentStyle'));
  assert.ok(!R.screen({ name: 'Buckeye DOT Advisors' }, []).reasons.some((h) => h.key === 'governmentStyle'));
});

test('description: naming an agency is fine, claiming to be or act for one is flagged', () => {
  const gov = (description, name = 'Acme Safety') => R.screen({ name, description }, []).reasons.some((h) => h.key === 'governmentStyle');
  // Honest experience, common among real consultants: not flagged
  assert.equal(gov('Run by a former FMCSA investigator with 17 years of experience'), false);
  assert.equal(gov('We help carriers with Department of Transportation audits and USDOT filings'), false);
  assert.equal(gov('Registered FMCSA process agent'), false);
  // Claims to be, or speak for, the government: flagged
  assert.equal(gov('Official FMCSA filing service'), true);
  assert.equal(gov('We are a government agency processing your update'), true);
  assert.equal(gov('Filing on behalf of the DOT'), true);
  assert.equal(gov('FMCSA-approved compliance program'), true);
  // Business name still flagged on any government word
  assert.equal(gov('', 'FMCSA Compliance Services LLC'), true);
  assert.equal(R.screen({ name: 'DOT Authority Filings' }, []).band, 'check');
});
