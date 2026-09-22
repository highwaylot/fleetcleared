(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
  const initials = (name) => name.split(/\s+/).filter(w => /^[A-Za-z]/.test(w)).slice(0, 2).map(w => w[0].toUpperCase()).join('');

  function el(tag, props = {}, children = []) {
    const node = Object.assign(document.createElement(tag), props);
    node.append(...children);
    return node;
  }

  // Sample listings for the design preview. Replaced by real approved listings from the database later.
  const consultants = [
    { name: 'Midwest DOT Advisors', states: ['OH', 'IN', 'KY'], region: 'Ohio, Indiana, Kentucky', hasLogo: false,
      desc: 'Driver qualification files, HOS audits, and drug & alcohol program setup for 1–15 truck fleets.', tags: ['DQ Files', 'Audits', 'Drug & Alcohol'] },
    { name: 'Lone Star Compliance Group', states: ['TX', 'OK'], region: 'Texas, Oklahoma', hasLogo: true,
      desc: 'Full-service FMCSA compliance for owner-operators. Se habla español.', tags: ['Owner-Operators', 'Bilingual', 'New Entrant Audits'] },
    { name: 'Southeast Fleet Safety Co.', states: ['GA', 'FL', 'AL'], region: 'Georgia, Florida, Alabama', hasLogo: false,
      desc: 'Post-audit corrective action plans and CSA score recovery.', tags: ['CSA Scores', 'Audits'] },
    { name: 'Great Plains Carrier Services', states: ['KS', 'NE', 'OK'], region: 'Kansas, Nebraska, Oklahoma', hasLogo: false,
      desc: 'New authority setup, BOC-3 guidance, and first-year safety program for new carriers.', tags: ['New Entrant Audits', 'DQ Files'] },
  ];

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
        const btn = el('button', { className: 'btn btn-primary', type: 'button', textContent: 'Request contact' });
        btn.addEventListener('click', () => openContact(c.name));
        return el('article', { className: 'card' }, [
          el('div', { className: 'card-id' }, [
            el('div', { className: 'org-logo' + (c.hasLogo ? '' : ' placeholder'), textContent: initials(c.name), ariaHidden: 'true' }),
            el('div', {}, [el('h2', { textContent: c.name }), el('p', { className: 'region', textContent: c.region })]),
          ]),
          el('p', { className: 'desc', textContent: c.desc }),
          el('div', { className: 'tags' }, c.tags.map(t => el('span', { className: 'tag', textContent: t }))),
          btn,
        ]);
      }));
      $('#result-count').textContent = `${matches.length} consultant${matches.length === 1 ? '' : 's'} listed`;
      $('#empty').hidden = matches.length > 0;
    };
    [state, spec].forEach(s => s.addEventListener('change', render));
    q.addEventListener('input', render);
    render();
  }

  // Request-contact modal
  const modal = $('#contact-modal');
  let lastFocus = null;
  function openContact(name) {
    lastFocus = document.activeElement;
    $('#contact-to').textContent = name;
    $('#contact-form').reset();
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

  // Admin tabs
  $$('.tabs [role=tab]').forEach(tab => tab.addEventListener('click', () => {
    $$('.tabs [role=tab]').forEach(t => {
      const on = t === tab;
      t.setAttribute('aria-selected', String(on));
      $('#' + t.getAttribute('aria-controls')).hidden = !on;
    });
  }));
})();
