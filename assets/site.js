(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
  const initials = (name) => name.split(/\s+/).filter(w => /^[A-Za-z]/.test(w)).slice(0, 2).map(w => w[0].toUpperCase()).join('');

  function el(tag, props = {}, children = []) {
    const node = Object.assign(document.createElement(tag), props);
    node.append(...children);
    return node;
  }
  function svg(markup, cls = '') {
    const wrap = document.createElement('span');
    wrap.innerHTML = markup;
    const node = wrap.firstChild;
    if (cls) node.setAttribute('class', cls);
    return node;
  }

  // Per-visitor conveniences only (remembered contact details, a signup draft). Storage can be blocked, so every call is guarded.
  const store = {
    get(k) { try { return JSON.parse(localStorage.getItem(k)); } catch { return null; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* storage unavailable */ } },
    del(k) { try { localStorage.removeItem(k); } catch { /* storage unavailable */ } },
  };
  const openInfo = (c) => (window.FCHours && c.hours ? window.FCHours.openStatus(c.hours, c.tz) : null);
  const digitsOnly = (v) => v.replace(/\D/g, '');
  function formatPhone(v) {
    const d = digitsOnly(v).replace(/^1(?=\d{10})/, '').slice(0, 10);
    if (d.length < 4) return d;
    if (d.length < 7) return `(${d.slice(0, 3)}) ${d.slice(3)}`;
    return `(${d.slice(0, 3)}) ${d.slice(3, 6)}-${d.slice(6)}`;
  }

  const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  const VIA = {
    call: { label: 'Phone call', field: 'Phone number', type: 'tel', auto: 'tel',
      icon: '<svg viewBox="0 0 24 24"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>' },
    text: { label: 'Text message', field: 'Mobile number', type: 'tel', auto: 'tel',
      icon: '<svg viewBox="0 0 24 24"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/></svg>' },
    email: { label: 'Email', field: 'Email address', type: 'email', auto: 'email',
      icon: '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>' },
  };

  // Listings: the demo pages load assets/demo-data.js and hand us the full rich shape directly.
  // The live site has no demo flag, so we fetch real approved listings from the API instead and
  // adapt their thinner intake-form shape (free-text states/specialties/hours, no reviews or logo
  // yet) into the same shape the rendering code below already expects.
  function mapListing(r) {
    const states = String(r.states || '').split(/[,\s]+/).filter(Boolean).map(s => s.toUpperCase());
    const tags = String(r.specialties || '').split(',').map(s => s.trim()).filter(Boolean).slice(0, 4);
    const approvedYear = r.approvedAt ? new Date(Number(r.approvedAt) * 1000).getFullYear() : '';
    return {
      slug: r.id, name: r.name || 'Unnamed listing', states, tags,
      desc: r.description || '', about: r.description || '',
      region: states.join(', ') || 'Service area not listed',
      hasLogo: false,
      prefer: r.contactPref || 'call',
      tz: r.timezone ? `${r.timezone} Time` : 'Central Time',
      // No structured per-day hours from the intake form yet, so open/closed can't be computed;
      // the free-text hours the consultant gave shows as their "response" note instead.
      hours: [null, null, null, null, null, null, null],
      response: r.hours || 'Contact for hours',
      langs: 'English',
      since: approvedYear ? String(approvedYear) : '',
      atLimit: Boolean(r.atLimit), resumes: 'next month',
      reviews: [],
    };
  }

  const avg = (c) => c.reviews.length ? c.reviews.reduce((s, r) => s + r.stars, 0) / c.reviews.length : 0;
  const STAR = '<svg viewBox="0 0 20 20"><path d="M10 1.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L10 14.8l-5.2 2.8 1-5.8L1.5 7.7l5.9-.9z"/></svg>';
  function stars(n) {
    const box = el('span', { className: 'stars', role: 'img', ariaLabel: `${n.toFixed(1)} out of 5 stars` });
    for (let i = 1; i <= 5; i++) box.append(svg(STAR, i <= Math.round(n) ? 'on' : 'off'));
    return box;
  }
  const ratingText = (c) => c.reviews.length
    ? `${avg(c).toFixed(1)} ★ (${c.reviews.length} review${c.reviews.length === 1 ? '' : 's'})`
    : 'No reviews yet';

  // A consultant at their monthly lead limit can't receive requests until it resets.
  function contactButton(c, big = false) {
    const btn = el('button', { className: 'btn btn-primary' + (big ? ' btn-lg' : ''), type: 'button' });
    if (c.atLimit) {
      btn.disabled = true;
      btn.textContent = `Not taking requests until ${c.resumes}`;
    } else {
      btn.textContent = 'Request contact';
      btn.addEventListener('click', () => openContact(c));
    }
    return btn;
  }

  // Browse page and consultant profile page both need the consultant list before they can render
  // anything, and that list now arrives asynchronously on the live site (a fetch), synchronously
  // on the demo (window.FC_DEMO_CONSULTANTS). Everything that reads `consultants` lives in this
  // one function so either path can call it once the data is actually in hand.
  function initListings(consultants) {
  const bySlug = Object.fromEntries(consultants.map(c => [c.slug, c]));

  // Browse page
  const grid = $('#grid');
  if (grid) {
    const state = $('#f-state'), specToggle = $('#f-spec-toggle'), specPanel = $('#f-spec-panel'), q = $('#f-q'), sort = $('#f-sort'), onlyOpen = $('#f-open'), clear = $('#f-clear');
    const specAll = specPanel.querySelector('[data-all]');
    const specBoxes = [...specPanel.querySelectorAll('input:not([data-all])')];
    const qsState = new URLSearchParams(location.search).get('state');
    if (qsState && [...state.options].some(o => o.value === qsState.toUpperCase())) state.value = qsState.toUpperCase();
    const SORTS = {
      rating: (a, b) => avg(b) - avg(a) || b.reviews.length - a.reviews.length,
      reviews: (a, b) => b.reviews.length - a.reviews.length || avg(b) - avg(a),
      name: (a, b) => a.name.localeCompare(b.name),
    };
    // Consultants type their own specialty tags free-text, so they rarely match this fixed list
    // exactly ("DQ files" vs "DQ Files"). Match case-insensitively in either direction instead.
    const specMatch = (tag, selected) => {
      const t = tag.toLowerCase(), s = selected.toLowerCase();
      return t.includes(s) || s.includes(t);
    };
    const selectedSpecs = () => specBoxes.filter(b => b.checked).map(b => b.value);
    const updateSpecToggle = () => {
      const chosen = selectedSpecs();
      specToggle.textContent = chosen.length === 0 ? 'All specialties' : chosen.length === 1 ? chosen[0] : `${chosen.length} specialties`;
    };
    specAll.addEventListener('change', () => {
      if (specAll.checked) specBoxes.forEach(b => b.checked = false);
      updateSpecToggle(); render();
    });
    specBoxes.forEach(b => b.addEventListener('change', () => {
      if (b.checked) specAll.checked = false;
      if (specBoxes.every(x => !x.checked)) specAll.checked = true;
      updateSpecToggle(); render();
    }));
    specToggle.addEventListener('click', () => {
      const open = specPanel.hidden;
      specPanel.hidden = !open;
      specToggle.setAttribute('aria-expanded', String(open));
    });
    document.addEventListener('click', (e) => {
      if (!specPanel.hidden && !e.target.closest('#f-spec')) { specPanel.hidden = true; specToggle.setAttribute('aria-expanded', 'false'); }
    });
    const render = () => {
      const needle = q.value.trim().toLowerCase();
      const chosenSpecs = selectedSpecs();
      const matches = consultants.filter(c =>
        (!state.value || c.states.includes(state.value)) &&
        (chosenSpecs.length === 0 || chosenSpecs.some(sel => c.tags.some(t => specMatch(t, sel)))) &&
        (!onlyOpen.checked || !c.atLimit) &&
        (!needle || c.name.toLowerCase().includes(needle))).sort(SORTS[sort.value]);
      clear.hidden = !(state.value || chosenSpecs.length || needle || onlyOpen.checked);
      grid.replaceChildren(...matches.map(c => {
        const btn = contactButton(c);
        const href = `consultant.html#${c.slug}`;
        return el('article', { className: 'card' }, [
          el('div', { className: 'card-id' }, [
            el('div', { className: 'org-logo' + (c.hasLogo ? '' : ' placeholder'), textContent: initials(c.name), ariaHidden: 'true' }),
            el('div', {}, [
              el('h2', {}, [el('a', { href, textContent: c.name })]),
              el('p', { className: 'region', textContent: `${c.states.join(', ')} · ${ratingText(c)}` }),
            ]),
          ]),
          ...(() => { const o = openInfo(c); return o ? [el('p', { className: 'open-chip' + (o.open ? ' is-open' : ''), textContent: c.atLimit ? `Not taking requests until ${c.resumes}` : o.text })] : []; })(),
          el('p', { className: 'desc', textContent: c.desc }),
          el('div', { className: 'tags' }, c.tags.map(t => el('span', { className: 'tag', textContent: t }))),
          el('div', { className: 'card-actions' }, [el('a', { className: 'btn btn-ghost', href, textContent: 'View profile' }), btn]),
        ]);
      }));
      $('#result-count').textContent = `${matches.length} consultant${matches.length === 1 ? '' : 's'} listed`;
      $('#result-count').hidden = consultants.length === 0;
      $('#empty').hidden = matches.length > 0 || consultants.length === 0;
      $('#empty-launch').hidden = consultants.length > 0;
    };
    [state, sort, onlyOpen].forEach(s => s.addEventListener('change', render));
    q.addEventListener('input', render);
    clear.addEventListener('click', () => {
      state.value = ''; q.value = ''; onlyOpen.checked = false;
      specBoxes.forEach(b => b.checked = false); specAll.checked = true; updateSpecToggle();
      render();
      q.focus();
    });
    updateSpecToggle();
    render();
  }

  // Consultant profile page
  const profile = $('#p-name');
  if (profile) {
    const c = bySlug[location.hash.slice(1)];
    if (!c) {
      $('#profile-page').hidden = true;
      $('#profile-missing').hidden = false;
      return;
    }
    document.title = `${c.name} | FleetCleared`;
    const logo = $('#p-logo');
    logo.textContent = initials(c.name);
    logo.classList.toggle('placeholder', !c.hasLogo);
    profile.textContent = c.name;
    $('#p-region').textContent = c.region;
    $('#p-rating-link').textContent = ratingText(c);
    $('#p-about').textContent = c.about;
    $('#p-tags').replaceChildren(...c.tags.map(t => el('span', { className: 'tag', textContent: t })));
    $('#p-states').replaceChildren(...c.states.map(t => el('span', { className: 'tag', textContent: t })));
    $('#p-pref').replaceChildren(svg(VIA[c.prefer].icon), VIA[c.prefer].label);
    $('#p-response').textContent = c.response;
    $('#p-langs').textContent = c.langs;
    $('#p-since').textContent = c.since;
    $('#p-tz').textContent = `All times ${c.tz}`;
    const status = openInfo(c);
    const today = status ? status.today : (new Date().getDay() + 6) % 7;
    const chipText = c.atLimit ? `Not taking requests until ${c.resumes}` : (status ? status.text : '');
    for (const id of ['#p-open-chip', '#p-open-line']) {
      $(id).textContent = chipText;
      $(id).classList.toggle('is-open', Boolean(status && status.open && !c.atLimit));
    }
    $('#p-mobile-name').textContent = c.name;
    $('#p-mobile-open').textContent = c.atLimit ? '' : chipText;
    const barBtn = contactButton(c);
    if (c.atLimit) barBtn.textContent = `Back ${c.resumes}`;
    $('#p-mobile-btn').replaceWith(barBtn);
    $('#p-hours').replaceChildren(...DAYS.map((d, i) => el('tr', { className: [i === today ? 'today' : '', c.hours[i] ? '' : 'closed'].join(' ').trim() }, [
      el('td', { textContent: i === today ? `${d} (today)` : d }),
      el('td', { textContent: c.hours[i] || 'Closed' }),
    ])));
    $('#p-contact').replaceWith(contactButton(c, true));
    $('#p-limit').hidden = !c.atLimit;
    if (c.atLimit) $('#p-limit-date').textContent = c.resumes;

    const n = c.reviews.length;
    $('#p-review-count').textContent = n ? `(${n})` : '';
    $('#p-avg').textContent = n ? avg(c).toFixed(1) : '–';
    $('#p-avg-stars').replaceWith(stars(avg(c)));
    $('#p-total').textContent = n ? `${n} review${n === 1 ? '' : 's'}` : 'No reviews yet';
    $('#p-bars').replaceChildren(...[5, 4, 3, 2, 1].map(k => {
      const count = c.reviews.filter(r => r.stars === k).length;
      return el('div', { className: 'bar-row' }, [
        el('span', { textContent: `${k}★` }),
        el('span', { className: 'bar' }, [el('i', { style: `width:${n ? (count / n) * 100 : 0}%` })]),
        el('span', { textContent: String(count) }),
      ]);
    }));
    const REVIEW_SORTS = { newest: () => 0, lowest: (a, b) => a.stars - b.stars, highest: (a, b) => b.stars - a.stars };
    const renderReviews = () => $('#p-review-list').replaceChildren(...(n ? [...c.reviews].sort(REVIEW_SORTS[$('#p-review-sort').value]).map(r => el('article', { className: 'panel review' }, [
      el('div', { className: 'review-head' }, [
        el('span', { className: 'avatar', textContent: initials(r.who), ariaHidden: 'true' }),
        el('div', { className: 'review-who' }, [el('b', { textContent: r.who }), el('span', { textContent: `${r.role} · ${r.when}` })]),
        el('span', { className: 'verified', textContent: 'Identity confirmed' }),
      ]),
      stars(r.stars),
      el('p', { textContent: r.text }),
      ...(r.reply ? [el('div', { className: 'reply' }, [el('b', { textContent: `Reply from ${c.name}` }), r.reply])] : []),
    ])) : [el('p', { className: 'panel', textContent: 'No reviews yet. Reviews come only from carriers who contacted this consultant through FleetCleared.' })]));
    renderReviews();
    $('#p-review-sort').addEventListener('change', renderReviews);
    $('.review-tools').hidden = n < 2;

    const showTab = (name) => {
      $$('.profile-tabs [role=tab]').forEach(t => {
        const on = t.getAttribute('aria-controls') === name;
        t.setAttribute('aria-selected', String(on));
        $('#' + t.getAttribute('aria-controls')).hidden = !on;
      });
    };
    $$('.profile-tabs [role=tab]').forEach(t => t.addEventListener('click', () => showTab(t.getAttribute('aria-controls'))));
    $('#p-rating-link').addEventListener('click', e => {
      e.preventDefault();
      showTab('reviews');
      $('.profile-tabs').scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }
  }

  // Demo pages hand us the full rich shape straight away. Live pages have no demo flag, so they
  // fetch real approved listings and adapt them with mapListing() before rendering the same way.
  if (window.FC_DEMO_CONSULTANTS) {
    initListings(window.FC_DEMO_CONSULTANTS);
  } else if ($('#grid') || $('#p-name')) {
    fetch('/api/consultants_public')
      .then(res => res.json())
      .then(data => initListings(((data && data.rows) || []).map(mapListing)))
      .catch(() => initListings([]));
  }

  // Request-contact modal
  const modal = $('#contact-modal');
  let lastFocus = null;
  let currentContact = null;
  function setVia(via) {
    const v = VIA[via], input = $('#cf-contact');
    $('#cf-contact-label').textContent = v.field;
    if (input.type !== v.type) input.value = '';
    input.type = v.type;
    showContactError('');
    input.autocomplete = v.auto;
    $('#cf-text-consent').hidden = via !== 'text';
  }
  function showContactError(msg) {
    const err = $('#cf-contact-error');
    if (!err) return;
    err.textContent = msg;
    err.hidden = !msg;
    $('#cf-contact').setAttribute('aria-invalid', String(Boolean(msg)));
  }
  function contactError() {
    const input = $('#cf-contact');
    const v = input.value.trim();
    if (!v) return input.type === 'email' ? 'Enter your email address.' : 'Enter your phone number.';
    if (input.type === 'email') return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v) ? '' : 'That email address looks incomplete. Check for a typo.';
    return digitsOnly(v).length === 10 || (digitsOnly(v).length === 11 && digitsOnly(v)[0] === '1') ? '' : 'Enter a 10-digit phone number, area code first.';
  }
  function fillRemembered() {
    const saved = store.get('fc-carrier');
    $('#cf-remembered').hidden = !saved;
    if (!saved) return;
    $('#cf-name').value = saved.name || '';
    $('#cf-co').value = saved.company || '';
    if (saved.fleet) $('#cf-fleet').value = saved.fleet;
  }
  function openContact(c) {
    currentContact = c;
    lastFocus = document.activeElement;
    $('#contact-to').textContent = c.name;
    $$('.cf-to-name').forEach(n => { n.textContent = c.name; });
    $('#contact-form').reset();
    $(`#cf-via-${c.prefer}`).checked = true;
    setVia(c.prefer);
    $('#cf-pref-note').textContent = `${c.name} prefers ${VIA[c.prefer].label.toLowerCase()}. Pick whatever works for you.`;
    fillRemembered();
    $('#contact-form').hidden = false;
    $('#contact-done').hidden = true;
    modal.hidden = false;
    ($('#cf-name').value ? $('#cf-contact') : $('#cf-name')).focus();
  }
  function closeContact() {
    modal.hidden = true;
    lastFocus?.focus();
  }
  if (modal) {
    $$('input[name="cf-via"]').forEach(r => r.addEventListener('change', () => setVia(r.value)));
    $$('[data-close]', modal).forEach(b => b.addEventListener('click', closeContact));
    modal.addEventListener('click', e => { if (e.target === modal) closeContact(); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && !modal.hidden) closeContact(); });
    // Phone numbers are tidied when the field is left, never while typing, so the cursor never jumps.
    $('#cf-contact').addEventListener('input', () => { if (!$('#cf-contact-error').hidden) showContactError(contactError()); });
    $('#cf-contact').addEventListener('blur', e => {
      if (e.target.type === 'tel' && digitsOnly(e.target.value).length >= 10) e.target.value = formatPhone(e.target.value);
      if (e.target.value) showContactError(contactError());
    });
    $('#cf-forget').addEventListener('click', () => {
      store.del('fc-carrier');
      ['#cf-name', '#cf-co'].forEach(sel => { $(sel).value = ''; });
      $('#cf-fleet').value = '';
      $('#cf-remembered').hidden = true;
      $('#cf-name').focus();
    });
    $('#contact-form').addEventListener('submit', async e => {
      e.preventDefault();
      const msg = contactError();
      showContactError(msg);
      if (msg) { $('#cf-contact').focus(); return; }
      if (!currentContact) return;
      store.set('fc-carrier', { name: $('#cf-name').value.trim(), company: $('#cf-co').value.trim(), fleet: $('#cf-fleet').value });
      const submitBtn = $('#contact-form button[type=submit]');
      if (submitBtn) submitBtn.disabled = true;
      let result;
      try {
        const res = await fetch('/api/lead_request', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            consultantId: currentContact.slug,
            name: $('#cf-name').value.trim(),
            company: $('#cf-co').value.trim(),
            fleet: Number($('#cf-fleet').value),
            via: (document.querySelector('input[name="cf-via"]:checked') || {}).value || 'call',
            contact: $('#cf-contact').value.trim(),
            need: $('#cf-need') ? $('#cf-need').value.trim() : '',
          }),
        });
        result = await res.json();
      } catch (err) {
        result = { ok: false, error: 'network' };
      }
      if (submitBtn) submitBtn.disabled = false;
      if (result && result.ok) {
        $('#contact-form').hidden = true;
        $('#contact-done').hidden = false;
      } else if (result && result.error === 'not_accepting') {
        showContactError("This consultant isn't taking new requests right now. Try another consultant.");
      } else {
        showContactError("Something went wrong sending your request. Try again in a moment.");
      }
    });
  }

  // For-consultants signup
  const listForm = $('#list-form');
  if (listForm) {
    const preview = $('#logo-preview');
    const FIELDS = ['lf-name', 'lf-email', 'lf-phone', 'lf-pref', 'lf-tz', 'lf-cap', 'lf-hours', 'lf-spec', 'lf-desc'];
    const PREF = { call: 'Prefers a phone call', text: 'Prefers text messages', email: 'Prefers email' };
    const statesPanel = $('#lf-states-panel'), statesToggle = $('#lf-states-toggle');
    const statesBoxes = statesPanel ? [...statesPanel.querySelectorAll('input')] : [];
    const checkedStates = () => statesBoxes.filter(b => b.checked).map(b => b.value);
    const updateStatesToggle = () => {
      const chosen = checkedStates();
      statesToggle.textContent = chosen.length === 0 ? 'Choose states' : chosen.length <= 3 ? chosen.join(', ') : `${chosen.length} states`;
    };
    if (statesToggle) {
      statesToggle.addEventListener('click', () => {
        const open = statesPanel.hidden;
        statesPanel.hidden = !open;
        statesToggle.setAttribute('aria-expanded', String(open));
      });
      document.addEventListener('click', (e) => {
        if (!statesPanel.hidden && !e.target.closest('#lf-states')) { statesPanel.hidden = true; statesToggle.setAttribute('aria-expanded', 'false'); }
      });
      statesBoxes.forEach(b => b.addEventListener('change', () => { updateStatesToggle(); updatePreview(); saveDraft(); }));
    }
    const updatePreview = () => {
      const name = $('#lf-name').value.trim();
      const states = checkedStates();
      const tags = $('#lf-spec').value.split(',').map(x => x.trim()).filter(Boolean).slice(0, 4);
      if (!preview.querySelector('img')) preview.textContent = initials(name) || '?';
      const pvLogo = $('#pv-logo');
      if (!pvLogo.querySelector('img')) pvLogo.textContent = initials(name) || '?';
      $('#pv-name').textContent = name || 'Your company';
      $('#pv-meta').textContent = `${states.length ? states.join(', ') : 'Your states'} · No reviews yet`;
      $('#pv-desc').textContent = $('#lf-desc').value.trim() || 'Your short description shows here.';
      $('#pv-tags').replaceChildren(...tags.map(t => el('span', { className: 'tag', textContent: t })));
      $('#pv-pref').textContent = PREF[$('#lf-pref').value];
      $('#lf-desc-count').textContent = String($('#lf-desc').value.length);
    };
    let saveTimer = null;
    const saveDraft = () => {
      clearTimeout(saveTimer);
      saveTimer = setTimeout(() => {
        const data = Object.fromEntries(FIELDS.map(id => [id, $('#' + id).value]));
        data['lf-states'] = checkedStates();
        store.set('fc-listing-draft', data);
        $('#lf-draft-note').hidden = false;
      }, 400);
    };
    const draft = store.get('fc-listing-draft');
    if (draft) {
      FIELDS.forEach(id => { if (draft[id] != null) $('#' + id).value = draft[id]; });
      if (Array.isArray(draft['lf-states'])) {
        statesBoxes.forEach(b => { b.checked = draft['lf-states'].includes(b.value); });
        updateStatesToggle();
      }
      $('#lf-draft-note').textContent = 'We restored your unfinished draft.';
      $('#lf-draft-note').hidden = false;
    }
    FIELDS.forEach(id => $('#' + id).addEventListener('input', () => { updatePreview(); saveDraft(); }));
    FIELDS.forEach(id => $('#' + id).addEventListener('change', () => { updatePreview(); saveDraft(); }));
    $('#lf-phone').addEventListener('blur', e => { if (digitsOnly(e.target.value).length >= 10) e.target.value = formatPhone(e.target.value); });
    updatePreview();
    $('#lf-logo').addEventListener('change', e => {
      const file = e.target.files[0];
      if (!file) return;
      const img = el('img', { alt: '' });
      img.src = URL.createObjectURL(file);
      preview.classList.remove('placeholder');
      preview.replaceChildren(img);
      const copy = img.cloneNode();
      $('#pv-logo').classList.remove('placeholder');
      $('#pv-logo').replaceChildren(copy);
    });
    listForm.addEventListener('submit', async e => {
      e.preventDefault();
      const err = $('#lf-error');
      err.hidden = true;
      // preventDefault() above skips the browser's native required-field check, so it has to be
      // triggered explicitly -- otherwise this silently submits with blank required fields.
      if (!listForm.reportValidity()) return;
      const phoneDigits = digitsOnly($('#lf-phone').value);
      if (!(phoneDigits.length === 10 || (phoneDigits.length === 11 && phoneDigits[0] === '1'))) {
        err.textContent = 'Enter a 10-digit phone number, area code first.';
        err.hidden = false;
        $('#lf-phone').focus();
        return;
      }
      if (checkedStates().length === 0) {
        err.textContent = 'Choose at least one state you serve.';
        err.hidden = false;
        statesToggle.focus();
        return;
      }
      // The Taste of FleetCleared demo loads demo-data.js, which sets this. Never let a demo
      // visitor's submission reach the real application store.
      if (window.FC_DEMO_CONSULTANTS) {
        store.del('fc-listing-draft');
        listForm.hidden = true;
        $('#lf-draft-note').hidden = true;
        $('#list-done').hidden = false;
        return;
      }
      const btn = listForm.querySelector('button[type=submit]');
      const label = btn.textContent;
      btn.disabled = true; btn.textContent = 'Submitting...';
      try {
        const body = {
          name: $('#lf-name').value.trim(), email: $('#lf-email').value.trim(), phone: $('#lf-phone').value.trim(),
          states: checkedStates().join(', '), contactPref: $('#lf-pref').value, timezone: $('#lf-tz').value,
          cap: $('#lf-cap').value, hours: $('#lf-hours').value.trim(), specialties: $('#lf-spec').value.trim(),
          description: $('#lf-desc').value.trim(), agree: $('#lf-agree').checked,
          botcheck: listForm.querySelector('[name=botcheck]').checked ? '1' : '',
        };
        const res = await fetch('/api/consultant_apply', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
        const data = await res.json().catch(() => ({}));
        if (!res.ok || data.ok === false) throw new Error(data.error || "That didn't send. Check your connection and try again.");
        store.del('fc-listing-draft');
        listForm.hidden = true;
        $('#lf-draft-note').hidden = true;
        $('#list-done').hidden = false;
      } catch (e2) {
        err.textContent = (e2 && e2.message) || "That didn't send. Check your connection and try again.";
        err.hidden = false;
        btn.disabled = false; btn.textContent = label;
      }
    });
  }

  // Lead prices on the consultant page come straight from the pricing rules.
  const priceRows = $('#price-rows');
  if (priceRows && window.FCRules) {
    priceRows.replaceChildren(...window.FCRules.PRICING.tiers.map(t =>
      el('tr', {}, [el('td', { textContent: t.label }), el('td', { textContent: `$${t.price}` })])));
  }

  // Monthly cost estimator on the consultant page, computed by the same pricing rules as real billing.
  const est = $('#estimator');
  if (est && window.FCRules) {
    const run = () => {
      const leads = Number($('#est-leads').value);
      const cap = $('#est-cap').value === '' ? null : Number($('#est-cap').value);
      const r = window.FCRules.estimateMonthly({ leadsPerMonth: leads, fleetSize: Number($('#est-fleet').value), monthlyCap: cap, freeLeadAvailable: true });
      $('#est-leads-out').textContent = String(leads);
      const declined = r.declined ? ` Your limit would decline ${r.declined} request${r.declined === 1 ? '' : 's'}, at no charge.` : '';
      $('#est-result').textContent = leads === 0
        ? 'No requests, no cost.'
        : `About $${r.total} for your first month: ${r.delivered} lead${r.delivered === 1 ? '' : 's'}, the first one free.${declined}`;
    };
    ['#est-leads', '#est-fleet', '#est-cap'].forEach(sel => $(sel).addEventListener('input', run));
    run();
  }

  // Second-look request on the application status page
  const appealForm = $('#appeal-form');
  if (appealForm) {
    appealForm.addEventListener('submit', e => {
      e.preventDefault();
      appealForm.hidden = true;
      $('#appeal-done').hidden = false;
    });
  }
})();
