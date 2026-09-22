// Admin preview: every score, reason and charge below is computed by assets/rules.js.
// Sample data only. In production these rows come from the database and the lookup services.
(() => {
  const R = window.FCRules;
  const $ = (s) => document.querySelector(s);
  const el = (tag, props = {}, kids = []) => { const n = Object.assign(document.createElement(tag), props); n.append(...kids); return n; };
  const pillFor = { clear: 'pill-ok', check: 'pill-trial', hold: 'pill-warn' };

  const existing = [
    { name: 'Midwest DOT Advisors', phone: '(614) 555-0100', address: '100 North High Street, Columbus OH', email: 'ops@midwestdot.com', ip: '10.0.0.5', signedUpAt: '2026-09-01', cardFingerprint: 'card_A', freeLeadUsed: true },
    { name: 'Lone Star Compliance Group', phone: '210-555-0199', address: '9 Alamo Rd, San Antonio TX', email: 'hi@lonestarcg.com', ip: '10.0.0.9', signedUpAt: '2026-06-01', cardFingerprint: 'card_B', freeLeadUsed: false },
    { name: 'Southeast Fleet Safety Co.', phone: '478-555-0123', address: '44 Cherry St, Macon GA', email: 'plans@sefleetsafety.com', ip: '10.0.1.2', signedUpAt: '2026-05-10', cardFingerprint: null, freeLeadUsed: true },
  ];

  const applicants = [
    { name: 'USA Trucking Compliance', email: 'info@usatruckingcompliance.com', website: 'https://www.usatruckingcompliance.com', phone: '800-555-0111', address: '12 Commerce Dr, Dallas TX', submitted: 'Sep 20', inStateRegistry: true, phoneLineType: 'landline', webPresenceFound: true, emailDomainAgeDays: 3000, ip: '10.2.2.2', signedUpAt: '2026-09-20' },
    { name: 'Commercial Truck Consulting', email: 'hello@gmail.com', phone: '614.555.0100', address: '7 Oak Ave, Columbus OH', submitted: 'Sep 21', inStateRegistry: true, phoneLineType: 'mobile', webPresenceFound: true, ip: '10.0.0.5', signedUpAt: '2026-09-21', appeal: { sent: 'Sep 22', text: 'We share an office suite and phone line with Midwest DOT Advisors, but we are a separate LLC. Our Ohio filing is linked below.', link: 'https://example.com/ohio-filing' } },
    { name: 'My Safety Manager LLC', email: 'contact@mysafetymanager.com', website: 'https://mysafetymanager.com', phone: '888-555-0177', address: '3 River Rd, Nashville TN', submitted: 'Sep 22', inStateRegistry: true, phoneLineType: 'landline', webPresenceFound: true, emailDomainAgeDays: 2400, associationMember: true, ip: '10.3.3.3', signedUpAt: '2026-09-22' },
    { name: 'Quick DOT Help', email: 'quickdothelp@yahoo.com', phone: '555-555-0199', address: '1 PO Box, Anytown', submitted: 'Sep 22', inStateRegistry: false, phoneLineType: 'voip', webPresenceFound: false, emailDomainAgeDays: 20, ip: '10.4.4.4', signedUpAt: '2026-09-22' },
  ];

  const results = applicants.map((a) => ({ a, r: R.screen(a, existing) }));

  $('#pending-rows').replaceChildren(...results.map(({ a, r }) => el('tr', {}, [
    el('td', {}, [el('b', { textContent: a.name }), ...(a.appeal ? [el('div', { className: 'hint', textContent: 'Asked for a second look' })] : [])]),
    el('td', { textContent: a.email }),
    el('td', { textContent: a.submitted }),
    el('td', {}, [
      el('span', { className: `pill ${pillFor[r.band]}`, textContent: `${r.bandLabel} · ${r.score}` }),
      ...(r.freeLeadAlreadyUsed ? [el('div', { className: 'hint', textContent: 'No free lead' })] : []),
    ]),
    el('td', {}, [r.reasons.length
      ? el('ul', { className: 'reasons' }, r.reasons.map((h) => el('li', { textContent: `${h.reason} (${h.points > 0 ? '+' : ''}${h.points})` })))
      : el('span', { className: 'hint', textContent: 'Nothing flagged' })]),
    el('td', {}, [el('div', { className: 'row-actions' }, [
      el('button', { className: 'btn btn-primary btn-sm', type: 'button', textContent: 'Approve' }),
      el('button', { className: 'btn btn-danger btn-sm', type: 'button', textContent: 'Reject' }),
    ])]),
  ])));

  const appeals = results.filter(({ a }) => a.appeal);
  $('#appeal-list').replaceChildren(...(appeals.length ? appeals.map(({ a, r }) => el('article', { className: 'panel appeal' }, [
    el('div', { className: 'appeal-head' }, [
      el('b', { textContent: a.name }),
      el('span', { className: `pill ${pillFor[r.band]}`, textContent: `${r.bandLabel} · ${r.score}` }),
      el('span', { className: 'hint', textContent: `Sent ${a.appeal.sent}` }),
    ]),
    el('p', { textContent: `“${a.appeal.text}”` }),
    el('p', { className: 'hint', textContent: `Link provided: ${a.appeal.link}` }),
    el('p', { className: 'hint', textContent: `Flagged for: ${r.reasons.map((h) => h.reason).join('; ')}` }),
    el('div', { className: 'row-actions' }, [
      el('button', { className: 'btn btn-primary btn-sm', type: 'button', textContent: 'Approve after review' }),
      el('button', { className: 'btn btn-ghost btn-sm', type: 'button', textContent: 'Ask for more info' }),
      el('button', { className: 'btn btn-danger btn-sm', type: 'button', textContent: 'Keep rejected' }),
    ]),
  ])) : [el('p', { className: 'hint', textContent: 'No requests right now.' })]));

  // Lead log: each row runs the real pricing decision for that consultant's account state at the time.
  const leads = [
    { date: 'Sep 21', consultant: 'Midwest DOT Advisors', carrier: 'L. Brooks · (740) 555-0133', trucks: 12, account: { freeLeadUsedByBusiness: true, cardOnFile: true, leadsThisMonth: 3, monthlyCap: 10 } },
    { date: 'Sep 19', consultant: 'Southeast Fleet Safety Co.', carrier: 'M. Ortiz · (229) 555-0170', trucks: 4, account: { freeLeadUsedByBusiness: true, cardOnFile: false, leadsThisMonth: 1, monthlyCap: 5 } },
    { date: 'Sep 18', consultant: 'Southeast Fleet Safety Co.', carrier: 'D. Alvarez · (912) 555-0142', trucks: 2, account: { freeLeadUsedByBusiness: false, cardOnFile: false, leadsThisMonth: 0, monthlyCap: 5 } },
    { date: 'Sep 10', consultant: 'Midwest DOT Advisors', carrier: 'T. Nguyen · tnguyen@qtrucking.com', trucks: 1, account: { freeLeadUsedByBusiness: false, cardOnFile: false, leadsThisMonth: 0, monthlyCap: 10 } },
    { date: 'Sep 5', consultant: 'Midwest DOT Advisors', carrier: 'R. Patel · (614) 555-0188', trucks: 6, account: { freeLeadUsedByBusiness: true, cardOnFile: true, leadsThisMonth: 1, monthlyCap: 10 } },
  ];
  const resultLabel = { deliver: 'Delivered', hold: 'Held: no card', decline: 'Declined: monthly limit' };
  let revenue = 0;
  $('#lead-rows').replaceChildren(...leads.map((l) => {
    const d = R.decideLead(l.account, l.trucks);
    revenue += d.charge;
    return el('tr', {}, [
      el('td', { textContent: l.date }), el('td', { textContent: l.consultant }), el('td', { textContent: l.carrier }),
      el('td', { textContent: String(l.trucks) }),
      el('td', { textContent: d.action === 'deliver' && d.charge === 0 ? 'Delivered: free lead' : resultLabel[d.action] }),
      el('td', { textContent: d.charge ? `$${d.charge}` : '—' }),
    ]);
  }));

  document.querySelectorAll('.tabs [role=tab]').forEach((tab) => tab.addEventListener('click', () => {
    document.querySelectorAll('.tabs [role=tab]').forEach((t) => {
      const on = t === tab;
      t.setAttribute('aria-selected', String(on));
      document.getElementById(t.getAttribute('aria-controls')).hidden = !on;
    });
  }));

  $('#stat-pending').textContent = String(results.length);
  $('#stat-appeals').textContent = String(appeals.length);
  $('#stat-leads').textContent = String(leads.length);
  $('#stat-revenue').textContent = `$${revenue}`;
})();
