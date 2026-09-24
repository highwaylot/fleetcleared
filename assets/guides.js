// Free tools on the guide pages: MCS-150 due date, audit readiness check, deadline reminder signup.
// Nothing here is saved or sent anywhere.
(function () {
  const $ = (s) => document.querySelector(s);
  const el = (tag, text, cls) => { const e = document.createElement(tag); if (text != null) e.textContent = text; if (cls) e.className = cls; return e; };
  // On the public soft launch the directory and reminders aren't open yet, so the tools don't link to them.
  const directoryOpen = document.documentElement.dataset.directory !== 'off';
  const fmt = (d) => d.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });

  // ---------- MCS-150 due date ----------
  const mcs = $('#mcs-form');
  if (mcs && window.FCDeadlines) {
    const input = $('#mcs-usdot'), err = $('#mcs-error'), out = $('#mcs-result');
    mcs.addEventListener('submit', (e) => {
      e.preventDefault();
      err.hidden = true;
      let r;
      try { r = window.FCDeadlines.mcs150NextDue(input.value); }
      catch (x) { err.textContent = x.message; err.hidden = false; out.hidden = true; input.focus(); return; }
      const when = r.thisMonth ? 'This month' : r.monthsAway === 1 ? 'Next month' : `In ${r.monthsAway} months`;
      out.replaceChildren(
        el('span', when, 'eyebrow'),
        el('p', `Due by ${fmt(r.dueBy)}`, 'tool-big'),
        el('p', `USDOT ${r.usdot} updates every ${r.month} of ${r.oddYears ? 'odd' : 'even'}-numbered years.`),
      );
      if (directoryOpen) { const a = el('a', 'Get a reminder before it’s due', 'btn btn-ghost'); a.href = 'guides.html#reminders'; out.append(a); }
      out.hidden = false;
    });
  }

  // ---------- Audit readiness check ----------
  const chk = $('#check-form');
  if (chk) {
    const labels = JSON.parse(chk.dataset.labels);
    const out = $('#check-result');
    const syncCdl = () => {
      const cdl = chk.querySelector('input[name="cdl"]:checked').value === 'yes';
      chk.querySelectorAll('fieldset.q[data-cdl="true"]').forEach((f) => { f.hidden = !cdl; });
    };
    chk.querySelectorAll('input[name="cdl"]').forEach((r) => r.addEventListener('change', syncCdl));
    syncCdl();
    chk.addEventListener('submit', (e) => {
      e.preventDefault();
      const fix = [], confirm = [], skipped = [];
      chk.querySelectorAll('fieldset.q[data-id]').forEach((f) => {
        if (f.hidden) return;
        const v = (f.querySelector('input:checked') || {}).value;
        if (v === 'no') fix.push(labels[f.dataset.id]);
        else if (v === 'unsure') confirm.push(labels[f.dataset.id]);
        else if (!v) skipped.push(labels[f.dataset.id]);
      });
      const list = (title, items, cls) => {
        if (!items.length) return null;
        const box = el('div', null, 'check-group ' + cls);
        box.append(el('h3', `${title} (${items.length})`));
        const ul = el('ul'); items.forEach((t) => ul.append(el('li', t))); box.append(ul);
        return box;
      };
      const head = fix.length
        ? el('p', `${fix.length} answer${fix.length > 1 ? 's' : ''} could fail an audit on ${fix.length > 1 ? 'their' : 'its'} own. Fix ${fix.length > 1 ? 'these' : 'this'} first.`, 'tool-big')
        : confirm.length || skipped.length ? el('p', 'No automatic-fail answers, but confirm the items below.', 'tool-big')
        : el('p', 'No automatic-fail answers. Keep the records that prove it.', 'tool-big');
      const next = el('p', null, 'check-next');
      const g = el('a', 'What to have ready for the audit'); g.href = 'guide-new-entrant-safety-audit.html';
      next.append(g);
      if (directoryOpen) { const b = el('a', 'Find a consultant', 'btn btn-primary'); b.href = 'browse.html'; next.append(' ', b); }
      out.replaceChildren(...[head, list('Could fail you automatically', fix, 'bad'), list('Not sure: check your records', confirm, 'warn'), list('Not answered', skipped, 'skip'), next].filter(Boolean));
      out.hidden = false;
      out.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }

  // ---------- Waitlists (email + optional fields, saved in our own Vercel KV store via /api/waitlist) ----------
  // Reused for the carrier form on the home page and the consultant form on for-consultants.html;
  // each form carries a data-kind of 'carrier' or 'consultant' so they land in separate lists.
  function wireWaitlist(form) {
    const kind = form.dataset.kind || 'carrier';
    const emailField = form.querySelector('[data-field=email]');
    const nameField = form.querySelector('[data-field=name]');
    const companyField = form.querySelector('[data-field=company]');
    const stateField = form.querySelector('[data-field=state]');
    const hp = form.querySelector('[name=botcheck]');
    const err = form.querySelector('.field-error');
    const done = document.getElementById(form.dataset.doneId);
    if (stateField && stateField.type === 'hidden') {
      try { const m = document.cookie.match(/(?:^|; )fc_state=([^;]+)/); if (m) stateField.value = decodeURIComponent(m[1]); } catch (e) {}
    }
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = emailField.value.trim();
      err.hidden = true;
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { err.textContent = 'Enter a full email address.'; err.hidden = false; emailField.focus(); return; }
      const btn = form.querySelector('button[type=submit]'); const label = btn.textContent; btn.disabled = true; btn.textContent = 'Sending...';
      try {
        const body = { kind, email, name: nameField ? nameField.value.trim() : '', company: companyField ? companyField.value.trim() : '', state: stateField ? stateField.value : '', botcheck: hp && hp.checked ? '1' : '' };
        const res = await fetch('/api/waitlist', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
        const data = await res.json().catch(() => ({}));
        if (!res.ok || data.ok === false) throw new Error(data.error || 'bad response');
        form.hidden = true; if (done) done.hidden = false;
      } catch (e2) {
        err.textContent = (e2 && e2.message) || 'That didn\'t send. Check your connection and try again.'; err.hidden = false;
        btn.disabled = false; btn.textContent = label;
      }
    });
  }
  document.querySelectorAll('.waitlist-form').forEach(wireWaitlist);

  // ---------- Reminder signup (preview: not connected) ----------
  const rem = $('#remind-form');
  if (rem) {
    const err = $('#r-error');
    rem.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = $('#r-email').value.trim(), phone = $('#r-phone').value.replace(/\D/g, ''), usdot = $('#r-usdot').value.trim();
      const picked = rem.querySelectorAll('input[name="d"]:checked').length;
      let msg = '';
      if (!email && !phone) msg = 'Enter an email or a mobile number so we know where to send reminders.';
      else if (email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) msg = 'That email doesn’t look complete. Check it and try again.';
      else if (phone && phone.length !== 10 && !(phone.length === 11 && phone[0] === '1')) msg = 'Enter a 10-digit mobile number.';
      else if (phone && !$('#r-text-ok').checked) msg = 'To get texts, check the box agreeing to text reminders. Or remove the number to get email only.';
      else if (!picked) msg = 'Pick at least one deadline.';
      else if (usdot && window.FCDeadlines) { try { window.FCDeadlines.cleanUsdot(usdot); } catch (x) { msg = x.message; } }
      err.textContent = msg; err.hidden = !msg;
      if (msg) return;
      rem.hidden = true; $('#r-done').hidden = false;
    });
  }
})();
