// FleetCleared business rules: per-lead pricing and consultant signup screening.
// Every number the business may want to change lives in PRICING or SCREENING below.
// Runs in the browser (window.FCRules) and in Node (require) so the same code is tested and shipped.
(function (root) {
  const PRICING = {
    tiers: [
      { label: '1–2 trucks', min: 1, max: 2, price: 30 },
      { label: '3–10 trucks', min: 3, max: 10, price: 45 },
      { label: '11+ trucks', min: 11, max: Infinity, price: 65 },
    ],
    floor: 25,
    ceiling: 90,
  };

  const SCREENING = {
    signals: {
      samePhone:        { points: 60, reason: (m) => `Same phone number as ${m}` },
      sameCard:         { points: 60, reason: (m) => `Same payment card as ${m}` },
      sameAddress:      { points: 40, reason: (m) => `Same business address as ${m}` },
      similarName:      { points: 25, reason: (m) => `Company name nearly matches ${m}` },
      sameRecentIp:     { points: 25, reason: (m) => `Signed up from the same internet address as ${m} within 30 days` },
      notInRegistry:    { points: 15, reason: () => 'Not found in the state business registry' },
      voipPhone:        { points: 15, reason: () => 'Phone is an internet or throwaway line' },
      newDomain:        { points: 10, reason: () => 'Email domain registered in the last 90 days' },
      freeEmail:        { points: 10, reason: () => 'Uses a free email address' },
      noWebPresence:    { points: 10, reason: () => 'No website or business listing found' },
      governmentStyle:  { points: 25, reason: () => 'Name or description may suggest a government agency' },
      domainMatchesSite:{ points: -10, reason: () => 'Email domain matches their website' },
      associationMember:{ points: -15, reason: () => 'Listed as a state trucking association member' },
    },
    bands: [
      { max: 24, key: 'clear', label: 'Clear' },
      { max: 59, key: 'check', label: 'Check' },
      { max: Infinity, key: 'hold', label: 'Hold' },
    ],
    nameSimilarity: 0.9,
    recentIpDays: 30,
    newDomainDays: 90,
    // Wording that can make a private business look like a government agency. 'DOT' alone is normal in this industry, so it isn't listed.
    governmentWords: /\b(department of transportation|fmcsa|federal motor carrier|usdot|u\.s\. dot|government|official|dot authority)\b/i,
    // In a description, naming an agency is normal ("former FMCSA investigator"). Only claims to BE or act FOR the government count.
    governmentClaims: /\b(official (fmcsa|usdot|dot|government|federal)|(a|an|the) (government|federal|state) agency|on behalf of (the )?(fmcsa|usdot|dot|department of transportation|government)|(affiliated|partnered) with (the )?(fmcsa|usdot|dot|department of transportation)|government[- ](approved|authorized|official)|(fmcsa|dot|usdot)[- ](approved|authorized|certified|official))\b/i,
    freeEmailDomains: ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com', 'icloud.com', 'live.com', 'msn.com', 'proton.me', 'protonmail.com'],
  };

  // ---------- helpers ----------
  const digits = (s) => String(s || '').replace(/\D/g, '');
  const normPhone = (s) => digits(s).slice(-10);
  const emailDomain = (e) => String(e || '').toLowerCase().split('@')[1] || '';
  const isFreeEmail = (e) => SCREENING.freeEmailDomains.includes(emailDomain(e));
  const siteDomain = (url) => String(url || '').toLowerCase().replace(/^https?:\/\//, '').replace(/^www\./, '').split('/')[0];

  const ADDRESS_WORDS = { street: 'st', avenue: 'ave', road: 'rd', boulevard: 'blvd', drive: 'dr', suite: 'ste', north: 'n', south: 's', east: 'e', west: 'w', highway: 'hwy', lane: 'ln', court: 'ct' };
  function normAddress(a) {
    return String(a || '').toLowerCase().replace(/[.,#]/g, ' ').split(/\s+/).filter(Boolean)
      .map((w) => ADDRESS_WORDS[w] || w).join(' ');
  }
  const NAME_NOISE = new Set(['llc', 'inc', 'co', 'corp', 'company', 'the', 'group', 'services', 'service']);
  function normName(n) {
    return String(n || '').toLowerCase().replace(/[^a-z0-9 ]/g, ' ').split(/\s+/).filter((w) => w && !NAME_NOISE.has(w)).join(' ');
  }
  // Dice coefficient on letter pairs: 1 = identical, 0 = nothing in common.
  function similarity(a, b) {
    a = normName(a).replace(/ /g, ''); b = normName(b).replace(/ /g, '');
    if (!a || !b) return 0;
    if (a === b) return 1;
    const pairs = (s) => { const m = new Map(); for (let i = 0; i < s.length - 1; i++) { const p = s.slice(i, i + 2); m.set(p, (m.get(p) || 0) + 1); } return m; };
    const pa = pairs(a), pb = pairs(b);
    let overlap = 0;
    for (const [p, n] of pa) overlap += Math.min(n, pb.get(p) || 0);
    return (2 * overlap) / (a.length - 1 + b.length - 1);
  }
  const daysBetween = (a, b) => Math.abs(new Date(a) - new Date(b)) / 86400000;

  // ---------- pricing ----------
  function tierFor(fleetSize) {
    const n = Number(fleetSize);
    if (!Number.isInteger(n) || n < 1) throw new Error('Fleet size must be a whole number of trucks, 1 or more');
    return PRICING.tiers.find((t) => n >= t.min && n <= t.max);
  }
  const leadPrice = (fleetSize) => tierFor(fleetSize).price;

  // What happens when a carrier sends a request to this consultant.
  // account: { freeLeadUsedByBusiness, cardOnFile, leadsThisMonth, monthlyCap (null = no limit) }
  function decideLead(account, fleetSize) {
    const price = leadPrice(fleetSize);
    if (!account.freeLeadUsedByBusiness) return { action: 'deliver', charge: 0, note: 'First lead for this business: free' };
    if (account.monthlyCap != null && account.leadsThisMonth >= account.monthlyCap) {
      return { action: 'decline', charge: 0, note: 'Monthly lead limit reached; tell the carrier this consultant is unavailable' };
    }
    if (!account.cardOnFile) return { action: 'hold', charge: 0, note: 'No card on file; hold up to 48 hours and ask the consultant to add one' };
    return { action: 'deliver', charge: price, note: `Charged $${price}` };
  }

  // Suggested re-price once real data exists: close rate × first-year client value × our cut, kept inside floor and ceiling.
  function suggestedPrice({ closeRate, clientValue, cut }) {
    for (const [k, v] of Object.entries({ closeRate, clientValue, cut })) {
      if (typeof v !== 'number' || !(v >= 0)) throw new Error(`${k} must be a number, 0 or more`);
    }
    const raw = closeRate * clientValue * cut;
    return Math.round(Math.min(PRICING.ceiling, Math.max(PRICING.floor, raw)));
  }


  // Rough monthly cost for the consultant-page estimator. Uses decideLead for every lead, so it can never disagree with real billing.
  // freeLeadAvailable: this business hasn't used its free lead yet. monthlyCap: null = no limit.
  function estimateMonthly({ leadsPerMonth, fleetSize, monthlyCap = null, freeLeadAvailable = false }) {
    if (!Number.isInteger(leadsPerMonth) || leadsPerMonth < 0) throw new Error('Leads per month must be a whole number, 0 or more');
    let total = 0, delivered = 0, declined = 0, freeUsed = !freeLeadAvailable;
    for (let i = 0; i < leadsPerMonth; i++) {
      const d = decideLead({ freeLeadUsedByBusiness: freeUsed, cardOnFile: true, leadsThisMonth: delivered, monthlyCap }, fleetSize);
      if (d.action === 'deliver') { delivered++; total += d.charge; if (!freeUsed) freeUsed = true; }
      else declined++;
    }
    return { delivered, declined, total };
  }

  // ---------- screening ----------
  // Two accounts are the same business (for the one free lead) if they share a phone, address, card, or company email domain.
  function sameBusiness(a, b) {
    if (normPhone(a.phone) && normPhone(a.phone) === normPhone(b.phone)) return true;
    if (normAddress(a.address) && normAddress(a.address) === normAddress(b.address)) return true;
    if (a.cardFingerprint && a.cardFingerprint === b.cardFingerprint) return true;
    const da = emailDomain(a.email);
    return Boolean(da) && !isFreeEmail(a.email) && da === emailDomain(b.email);
  }

  // applicant: fields from the signup form plus lookup results. A lookup that wasn't run is left undefined and never adds points.
  // existing: accounts already on FleetCleared.
  function screen(applicant, existing = []) {
    const S = SCREENING.signals;
    const hits = [];
    const hit = (key, match) => hits.push({ key, points: S[key].points, reason: S[key].reason(match) });

    const firstMatch = (test) => existing.find(test);
    const phone = normPhone(applicant.phone);
    const addr = normAddress(applicant.address);

    let m;
    if (phone && (m = firstMatch((e) => normPhone(e.phone) === phone))) hit('samePhone', m.name);
    if (applicant.cardFingerprint && (m = firstMatch((e) => e.cardFingerprint === applicant.cardFingerprint))) hit('sameCard', m.name);
    if (addr && (m = firstMatch((e) => normAddress(e.address) === addr))) hit('sameAddress', m.name);
    if ((m = firstMatch((e) => similarity(e.name, applicant.name) >= SCREENING.nameSimilarity))) hit('similarName', m.name);
    if (applicant.ip && applicant.signedUpAt && (m = firstMatch((e) => e.ip === applicant.ip && e.signedUpAt && daysBetween(e.signedUpAt, applicant.signedUpAt) <= SCREENING.recentIpDays))) hit('sameRecentIp', m.name);

    if (applicant.inStateRegistry === false) hit('notInRegistry');
    if (applicant.phoneLineType === 'voip') hit('voipPhone');
    if (typeof applicant.emailDomainAgeDays === 'number' && applicant.emailDomainAgeDays < SCREENING.newDomainDays) hit('newDomain');
    if (isFreeEmail(applicant.email)) hit('freeEmail');
    if (applicant.webPresenceFound === false) hit('noWebPresence');
    if (SCREENING.governmentWords.test(applicant.name || '') || SCREENING.governmentClaims.test(applicant.description || '')) hit('governmentStyle');
    if (applicant.website && !isFreeEmail(applicant.email) && emailDomain(applicant.email) === siteDomain(applicant.website)) hit('domainMatchesSite');
    if (applicant.associationMember === true) hit('associationMember');

    const score = Math.max(0, hits.reduce((s, h) => s + h.points, 0));
    const band = SCREENING.bands.find((b) => score <= b.max);
    const freeLeadAlreadyUsed = existing.some((e) => e.freeLeadUsed && sameBusiness(applicant, e));
    return { score, band: band.key, bandLabel: band.label, reasons: hits, freeLeadAlreadyUsed };
  }

  const api = { PRICING, SCREENING, tierFor, leadPrice, decideLead, suggestedPrice, estimateMonthly, screen, sameBusiness, similarity, normPhone, normAddress };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.FCRules = api;
})(typeof window !== 'undefined' ? window : globalThis);
