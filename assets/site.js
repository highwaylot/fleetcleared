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

  const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  const VIA = {
    call: { label: 'Phone call', field: 'Phone number', type: 'tel', auto: 'tel',
      icon: '<svg viewBox="0 0 24 24"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>' },
    text: { label: 'Text message', field: 'Mobile number', type: 'tel', auto: 'tel',
      icon: '<svg viewBox="0 0 24 24"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/></svg>' },
    email: { label: 'Email', field: 'Email address', type: 'email', auto: 'email',
      icon: '<svg viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>' },
  };

  // Listings: the demo pages load assets/demo-data.js; the live site starts empty until real listings come from the database.
  const consultants = window.FC_DEMO_CONSULTANTS || [];
  const bySlug = Object.fromEntries(consultants.map(c => [c.slug, c]));
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

  // Browse page
  const grid = $('#grid');
  if (grid) {
    const state = $('#f-state'), spec = $('#f-spec'), q = $('#f-q');
    const render = () => {
      const needle = q.value.trim().toLowerCase();
      const matches = consultants.filter(c =>
        (!state.value || c.states.includes(state.value)) &&
        (!spec.value || c.tags.includes(spec.value)) &&
        (!needle || c.name.toLowerCase().includes(needle)));
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
    [state, spec].forEach(s => s.addEventListener('change', render));
    q.addEventListener('input', render);
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
    const today = (new Date().getDay() + 6) % 7;
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
    $('#p-review-list').replaceChildren(...(n ? c.reviews.map(r => el('article', { className: 'panel review' }, [
      el('div', { className: 'review-head' }, [
        el('span', { className: 'avatar', textContent: initials(r.who), ariaHidden: 'true' }),
        el('div', { className: 'review-who' }, [el('b', { textContent: r.who }), el('span', { textContent: `${r.role} · ${r.when}` })]),
        el('span', { className: 'verified', textContent: 'Identity confirmed' }),
      ]),
      stars(r.stars),
      el('p', { textContent: r.text }),
      ...(r.reply ? [el('div', { className: 'reply' }, [el('b', { textContent: `Reply from ${c.name}` }), r.reply])] : []),
    ])) : [el('p', { className: 'panel', textContent: 'No reviews yet. Reviews come only from carriers who contacted this consultant through FleetCleared.' })]));

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

  // Request-contact modal
  const modal = $('#contact-modal');
  let lastFocus = null;
  function setVia(via) {
    const v = VIA[via], input = $('#cf-contact');
    $('#cf-contact-label').textContent = v.field;
    input.type = v.type;
    input.autocomplete = v.auto;
    $('#cf-text-consent').hidden = via !== 'text';
  }
  function openContact(c) {
    lastFocus = document.activeElement;
    $('#contact-to').textContent = c.name;
    $$('.cf-to-name').forEach(n => { n.textContent = c.name; });
    $('#contact-form').reset();
    $(`#cf-via-${c.prefer}`).checked = true;
    setVia(c.prefer);
    $('#cf-pref-note').textContent = `${c.name} prefers ${VIA[c.prefer].label.toLowerCase()}. Pick whatever works for you.`;
    $('#contact-form').hidden = false;
    $('#contact-done').hidden = true;
    modal.hidden = false;
    $('#cf-name').focus();
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
    $('#contact-form').addEventListener('submit', e => {
      e.preventDefault();
      $('#contact-form').hidden = true;
      $('#contact-done').hidden = false;
    });
  }

  // For-consultants signup
  const listForm = $('#list-form');
  if (listForm) {
    const preview = $('#logo-preview');
    $('#lf-name').addEventListener('input', e => {
      if (!preview.querySelector('img')) preview.textContent = initials(e.target.value) || '?';
    });
    $('#lf-logo').addEventListener('change', e => {
      const file = e.target.files[0];
      if (!file) return;
      const img = el('img', { alt: '' });
      img.src = URL.createObjectURL(file);
      preview.classList.remove('placeholder');
      preview.replaceChildren(img);
    });
    listForm.addEventListener('submit', e => {
      e.preventDefault();
      listForm.hidden = true;
      $('#list-done').hidden = false;
    });
  }

  // Lead prices on the consultant page come straight from the pricing rules.
  const priceRows = $('#price-rows');
  if (priceRows && window.FCRules) {
    priceRows.replaceChildren(...window.FCRules.PRICING.tiers.map(t =>
      el('tr', {}, [el('td', { textContent: t.label }), el('td', { textContent: `$${t.price}` })])));
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
