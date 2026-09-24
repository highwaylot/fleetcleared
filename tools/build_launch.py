# Public soft launch pages: home, terms of use and privacy for a site that collects no personal information.
# Run through tools/build_site.py with FC_LAUNCH=1. Values come from tools/launch.json; empty ones render as
# placeholders, and the build refuses to finish until they're filled.

CFG = json.loads((pathlib.Path(__file__).with_name("launch.json")).read_text())
def cfg(key):
    v = str(CFG.get(key, "")).strip()
    return v if v else fill(f"[{key.replace('_', ' ')}]")
NAME, FORMED, ADDRESS, COURTS, CAP, EFFECTIVE = (cfg(k) for k in ["legal_name", "state_of_formation", "mailing_address", "court_county_and_state", "liability_cap_dollars", "effective_date"])
# Blank web3forms_key just hides the waitlist section; it never blocks the build (unlike the fields above).

def launch_legal(fname, title, desc, h1, lede, summary_items, sections):
    toc = "".join(f'<li><a href="#{sid}">{st}</a></li>' for sid, st, _ in sections)
    body = "".join(f'<h2 id="{sid}">{st}</h2>{html}' for sid, st, html in sections)
    summ = "".join(f"<li>{icon(i)}<span>{t}</span></li>" for i, t in summary_items)
    write(fname, head(title, desc, fname) + header(None) + f'''<main class="wrap">
  <div class="page-head"><h1>{h1}</h1><p class="lede">{lede}</p></div>
  <div class="legal">
    <nav class="legal-toc" aria-label="On this page"><p>On this page</p><ol>{toc}</ol></nav>
    <article class="legal-body">
      <section class="summary"><h2>The short version</h2><ul>{summ}</ul></section>
      {body}
    </article>
  </div>
</main>
''' + FOOTER)

# ---------- HOME ----------
# Three, not all eight: the homepage's first screen is scanned, not read. A wall of equal-weight cards makes
# every item fight for attention (Hick's Law: more visible choices, slower decisions). guides.html already
# holds the complete, grouped index -- nothing here is otherwise unavailable, just not all dumped at once.
FEATURED_SLUGS = ["guide-new-entrant-safety-audit.html", "audit-readiness-check.html", "mcs-150-due-date.html"]
featured_cards = "".join(f'<a class="tour-card" href="{s}"><span class="variation">{g}</span><b>{c}</b><span>{b}</span></a>'
                          for s, c, b, g in RELATED_INDEX if s in FEATURED_SLUGS)
WAITLIST = f'''<section class="form-card wait-card" id="waitlist" aria-labelledby="wait-h">
  <h2 id="wait-h">Get first pick when we open</h2>
  <p>We\'ll email you once when consultants are live in your area. That\'s the only email you\'ll get from this list.</p>
  <form class="waitlist-form" data-kind="carrier" data-done-id="wait-done" novalidate>
    <input type="checkbox" name="botcheck" class="hp-field" tabindex="-1" autocomplete="off">
    <div class="field"><label for="wl-email">Email</label><input id="wl-email" data-field="email" type="email" autocomplete="email" required></div>
    <div class="field"><label for="wl-name">Name (optional)</label><input id="wl-name" data-field="name" type="text" autocomplete="name"></div>
    <input type="hidden" id="wl-state" data-field="state" value="">
    <p class="field-error" hidden></p>
    <button class="btn btn-primary" type="submit">Notify me</button>
  </form>
  <p class="notice" id="wait-done" hidden>You\'re on the list.</p>
  <p class="fine">We only use this to tell you the directory opened. See our <a href="privacy.html">privacy policy</a>.</p>
</section>'''
write("index.html", head("FleetCleared: Plain-Language DOT Compliance Guides for Small Trucking Companies",
  "Free guides and tools for small trucking companies: the new entrant safety audit, drug and alcohol testing, CSA warning letters and filing deadlines. Sources on every page.",
  "", f'''\n<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@graph": [
    {"@type": "Organization", "@id": f"{SITE}/#org", "name": "FleetCleared", "url": f"{SITE}/", "logo": f"{SITE}/assets/icons/icon-512.png"},
    {"@type": "WebSite", "@id": f"{SITE}/#site", "name": "FleetCleared", "url": f"{SITE}/", "publisher": {"@id": f"{SITE}/#org"}}]})}</script>''') + header(None) + f'''<main>
  <section class="hero wrap hero-launch">
    <span class="eyebrow">Free guides &amp; tools</span>
    <h1>Plain answers before a bad inspection finds you.</h1>
    <p class="lede">What the rules require, what fails a safety audit, and when things are due. Plain words, the official source linked on every page.</p>
    <div class="hero-actions">
      <a class="btn btn-primary btn-lg" href="guides.html">Read the guides</a>
      <a class="btn btn-ghost btn-lg" href="audit-readiness-check.html">Take the audit check</a>
    </div>
    <p class="trust-line"><span>No robocalls, ever</span><span>Sources on every page</span><span>Not affiliated with FMCSA</span></p>
  </section>
  <section class="wrap launch-guides">
    <p class="section-label eyebrow">Start here</p>
    <div class="tour-grid">{featured_cards}</div>
    <p class="fine" style="text-align:center">A directory of independent DOT compliance consultants is coming in 2027. <a href="guides.html">See every guide &amp; tool &rarr;</a></p>
    <p class="fine" style="text-align:center">DOT compliance consultant? <a href="for-consultants.html">Reserve a spot in the first wave &rarr;</a></p>
  </section>
  <section class="wrap">{WAITLIST}</section>
</main>
<script src="assets/guides.js" defer></script>
''' + FOOTER)

# ---------- TERMS OF USE ----------
launch_legal("terms.html", "Terms of Use | FleetCleared",
  "The terms for using FleetCleared's free compliance guides and tools.",
  "Terms of use", f"Effective {EFFECTIVE}. These terms apply to everyone who uses fleetcleared.com.",
  [("folder", "FleetCleared publishes <strong>general information</strong> about trucking compliance. It isn't legal or compliance advice."),
   ("search", "Rules change. <strong>Check the official sources</strong> we link, or a qualified professional, before you act."),
   ("scale", "Our tools give <strong>estimates</strong>. You're responsible for your own compliance and deadlines."),
   ("lock", "We don't collect personal information through the site. See our <a href=\"privacy.html\">privacy policy</a>.")],
  [
   ("who", "Who we are", f"<p>FleetCleared is operated by {NAME}, a {FORMED} company (\"FleetCleared,\" \"we,\" \"us\"). We publish guides and free tools about U.S. motor carrier safety rules. We are not a law firm or a compliance consultant, and we are not affiliated with the FMCSA or the U.S. Department of Transportation. By using the site you agree to these terms.</p>"),
   ("guides", "Guides and free tools", "<p>Our guides, the MCS-150 due-date tool and the audit readiness check are general information provided for convenience. They are not legal or compliance advice, they don't create a professional relationship with FleetCleared or anyone else, and they may be incomplete or out of date when rules change. Don't rely on them in place of the official regulations, FMCSA's own records and notices, or a qualified professional.</p><p>Tool results are estimates from the information you enter. The readiness check is a self-check, not an audit result, and answering \"yes\" to every question doesn't mean you'll pass an audit. Always confirm deadlines in your FMCSA registration and with the agency that sets them.</p><p>If you spot an error, tell us at <strong>corrections@fleetcleared.com</strong>. We review every report.</p>"),
   ("use", "Using the site", "<ul><li>You may read, print and share links to our pages for your own business use.</li><li>Don't copy or republish our guides in bulk, scrape the site, or present our content as your own.</li><li>Don't interfere with the site's security or operation.</li></ul><p>The guides, tools, design and FleetCleared name are ours. Regulations we quote belong to the public.</p>"),
   ("links", "Links to other sites", "<p>We link to government and industry sources so you can check what we say. We don't control those sites and aren't responsible for their content.</p>"),
   ("disclaimers", "Disclaimers", "<p>FleetCleared is provided \"as is\" and \"as available.\" To the fullest extent the law allows, we disclaim all warranties, express or implied, including warranties that our guides are accurate, complete or current, or that any tool result is correct.</p>"),
   ("liability", "Limitation of liability", f"<p>To the fullest extent the law allows, FleetCleared is not liable for indirect, incidental, special, consequential or punitive damages, or for lost profits, fines, penalties, failed audits or loss of operating authority, arising from your use of the site, our guides or our tools. Our total liability for any claim is limited to ${CAP}.</p>"),
   ("law", "Governing law", f"<p>These terms are governed by the laws of {FORMED}, without regard to conflict-of-law rules. Disputes will be resolved in the state or federal courts located in {COURTS}.</p>"),
   ("changes", "Changes", "<p>We may update these terms. We'll change the effective date at the top when we do. Continuing to use the site means you accept the updated terms.</p>"),
   ("contact", "Contact", f"<p><strong>legal@fleetcleared.com</strong><br>{NAME}, {ADDRESS}</p>"),
  ])

# ---------- PRIVACY ----------
launch_legal("privacy.html", "Privacy Policy | FleetCleared",
  "FleetCleared doesn't collect personal information through its guides and tools. What your browser shares when you visit.",
  "Privacy policy", f"Effective {EFFECTIVE}. The short answer: we don't ask for, collect or sell personal information.",
  [("ban", "No accounts, no forms, <strong>no advertising trackers</strong>, and we never sell information."),
   ("lock", "Our tools run <strong>on your device</strong>. What you type into them never reaches us."),
   ("share", "Like any website, our host and Google Fonts receive <strong>basic connection data</strong> such as your IP address.")],
  [
   ("collect", "What we collect", "<p>Nothing you type. The site has no sign-up, no contact form and no account. The MCS-150 due-date tool and the audit readiness check work entirely in your browser; your USDOT number and answers are never sent to us.</p>"),
   ("automatic", "What's shared automatically", "<p>When you load a page, your browser sends standard connection information, such as your IP address, browser type and the page requested. Our hosting provider receives it to deliver the site and protect it from attacks, and may keep it in short-term logs. Our pages also load fonts from Google Fonts, which receives your IP address when the font files load.</p><p>We use Vercel Web Analytics to count page views. It doesn't use cookies, doesn't track you across other websites, and doesn't build a profile of you. We only see aggregate numbers, like how many people read a page. We don't use advertising cookies or trackers.</p>"),
   ("email", "If you email us", "<p>If you email us, for example to report an error, we use your message and address only to reply and fix the problem, and we don't add you to any list.</p>"),
   ("waitlist", "If you sign up to be notified", "<p>If you enter your email (and optionally your name) to be notified when the consultant directory opens, we store it on our own server, hosted by Vercel, and use it only to send that one announcement, and to see which states people are asking from so we know where to launch next. We don't sell it, and we don't pass it to consultants or anyone else. Email <strong>privacy@fleetcleared.com</strong> to be removed at any time.</p>"),
   ("rights", "Your rights", "<p>Depending on where you live, you may have the right to ask what personal information we hold about you and to have it deleted. Since we don't collect it through the site, there's usually nothing to find, but email <strong>privacy@fleetcleared.com</strong> and we'll check within 45 days.</p>"),
   ("kids", "Children", "<p>FleetCleared is for businesses and isn't directed to anyone under 18.</p>"),
   ("contact", "Contact", f"<p><strong>privacy@fleetcleared.com</strong><br>{NAME}, {ADDRESS}</p>"),
  ])


# ---------- FOR CONSULTANTS (waitlist, not the real signup -- that needs a backend that doesn't exist yet) ----------
# The scarcity here is real, not invented: the launch plan targets a first wave of about 10-15 Texas
# consultants (see the field guide), and whoever lists first genuinely gets seen first while the
# directory is new and thin -- that advantage is structural, not a marketing trick, and goes away
# once more consultants join. Change FIRST_WAVE_SIZE if the plan changes.
FIRST_WAVE_SIZE = 15
consultant_page_ld = {"@context": "https://schema.org", "@type": "WebPage", "name": "FleetCleared for consultants", "url": f"{SITE}/for-consultants.html"}
write("for-consultants.html", head(
  "Be First in Texas | FleetCleared for DOT Compliance Consultants",
  "FleetCleared opens to a small first wave of Texas DOT compliance consultants. Reserve your spot before the directory fills in.",
  "for-consultants.html", f'\n<script type="application/ld+json">{json.dumps(consultant_page_ld)}</script>') + header("consultants") + f'''<main class="wrap">
  <section class="hero wrap hero-launch">
    <span class="eyebrow">For DOT compliance consultants</span>
    <h1>Texas carriers are already reading. You're not listed yet.</h1>
    <p class="lede">Every guide on this site ends with "find a consultant." Right now that page has nowhere to send them. The first wave of about {FIRST_WAVE_SIZE} Texas consultants gets listed while the directory is still new and thin -- seen first, not buried on page three once everyone else catches on.</p>
  </section>
  <section class="wrap" style="max-width:760px;margin-inline:auto">
    <div class="grid3" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin-bottom:8px">
      <div class="panel"><h3 style="margin:0 0 6px;font-size:18px">Free to list</h3><p class="hint" style="margin:0">Your first lead is free. After that, you pay only per lead, by fleet size.</p></div>
      <div class="panel"><h3 style="margin:0 0 6px;font-size:18px">First wave, first seen</h3><p class="hint" style="margin:0">Fewer listings means every one of them gets more attention. That window closes as we grow.</p></div>
      <div class="panel"><h3 style="margin:0 0 6px;font-size:18px">No robocalls, ever</h3><p class="hint" style="margin:0">Carriers only reach you when they ask to. We screen every signup by hand.</p></div>
    </div>
  </section>
  <section class="wrap">
    <section class="form-card wait-card" id="waitlist" aria-labelledby="cwait-h">
      <h2 id="cwait-h">Reserve your spot</h2>
      <p>We'll email you the moment the directory opens in your area, before it's public. No cost, no obligation to list.</p>
      <form class="waitlist-form" data-kind="consultant" data-done-id="cwait-done" novalidate>
        <input type="checkbox" name="botcheck" class="hp-field" tabindex="-1" autocomplete="off">
        <div class="form-grid">
          <div class="field"><label for="cwl-email">Email</label><input id="cwl-email" data-field="email" type="email" autocomplete="email" required></div>
          <div class="field"><label for="cwl-name">Your name</label><input id="cwl-name" data-field="name" type="text" autocomplete="name"></div>
          <div class="field full"><label for="cwl-company">Company (optional)</label><input id="cwl-company" data-field="company" type="text" autocomplete="organization"></div>
        </div>
        <input type="hidden" data-field="state" value="TX">
        <p class="field-error" hidden></p>
        <button class="btn btn-primary" type="submit">Reserve my spot</button>
      </form>
      <p class="notice" id="cwait-done" hidden>You're on the list. First wave, first seen.</p>
      <p class="fine">We only use this to tell you the directory opened, and to review your listing when you apply. See our <a href="privacy.html">privacy policy</a>.</p>
    </section>
  </section>
  {DISCLAIMER}
</main>
<script src="assets/guides.js" defer></script>
''' + FOOTER)


# ---------- PRIVATE STATUS PAGE (founder only: unguessable URL, never linked, noindex) ----------
# Change STATUS_SLUG any time you want a new private URL; the old one just stops working.
STATUS_SLUG = "status-3b3500e3.html"
ADMIN_SLUG = "waitlist-7f2c9a1d.html"  # defined here so the status page below can link to it
CONSULTANTS_ADMIN_SLUG = "consultants-9d4e1f2a.html"  # same idea: private, unguessable, noindex
status_cards = "".join(f'<a class="tour-card" href="{s}"><span class="variation">{g}</span><b>{c}</b><span>{b}</span></a>' for s, c, b, g in RELATED_INDEX)
status_page = head("FleetCleared Launch Status", "Private status page.", STATUS_SLUG).replace(
    '<link rel="canonical" href="https://fleetcleared.com/' + STATUS_SLUG + '">\n', "") + f"""<div class="preview-banner">Private page. Not linked anywhere on the site and blocked from search engines. Bookmark this URL; it isn't listed anywhere else.</div>
<header class="site-header"><div class="wrap">{LOGO}<span class="hint">Launch status</span></div></header>
<main class="wrap">
  <div class="page-head"><h1>Guides soft launch</h1><p class="lede">Every public page, plus where to check traffic. The guides collect nothing themselves, so real numbers live in Vercel.</p></div>
  <div class="tour">
    <section class="tour-section"><h2>Traffic and search</h2>
      <div class="tour-grid">
        <a class="tour-card" href="https://vercel.com/highwaylot/fleetcleared/analytics" rel="noopener"><span class="variation">Vercel</span><b>Page views by page</b><span>Needs Web Analytics turned on once in Vercel's dashboard (Analytics tab -&gt; Enable). Free tier, no cookies.</span></a>
        <a class="tour-card" href="https://search.google.com/search-console" rel="noopener"><span class="variation">Google</span><b>Search Console</b><span>Which guides show up in search and for what, once indexing is on and Google has crawled the site.</span></a>
      </div>
    </section>
    <section class="tour-section"><h2>Live pages</h2><div class="tour-grid"><a class="tour-card" href="index.html"><span class="variation">Home</span><b>fleetcleared.com</b><span>The guides landing page.</span></a>{status_cards}</div></section>
    <section class="tour-section"><h2>Waitlist</h2><div class="tour-grid"><a class="tour-card" href="{ADMIN_SLUG}"><span class="variation">Private</span><b>See who signed up</b><span>Every email and name, with a button to copy them all for a mass email once the directory opens.</span></a></div></section>
    <section class="tour-section"><h2>Consultant applications</h2><div class="tour-grid"><a class="tour-card" href="{CONSULTANTS_ADMIN_SLUG}"><span class="variation">Private</span><b>Review applications</b><span>Approve, reject, or ask for a second look. Screening score and reasons shown on each one.</span></a></div></section>
  </div>
</main>
"""
LAUNCH_PAGES.add(STATUS_SLUG)
write(STATUS_SLUG, status_page)


# ---------- PRIVATE WAITLIST ADMIN (founder only: reads api/admin_waitlist.py) ----------
# ADMIN_SLUG is set above, next to STATUS_SLUG. Separate from ADMIN_SECRET, which is a Vercel environment
# variable (Settings -> Environment Variables), never committed here -- set it, then open this page and
# enter that same value once; your browser remembers it after that.
admin_page = head("FleetCleared Waitlist", "Private waitlist admin.", ADMIN_SLUG).replace(
    '<link rel="canonical" href="https://fleetcleared.com/' + ADMIN_SLUG + '">\n', "") + f"""<div class="preview-banner">Private page. Not linked anywhere on the site and blocked from search engines.</div>
<header class="site-header"><div class="wrap">{LOGO}<span class="hint">Waitlist</span></div></header>
<main class="wrap">
  <div class="page-head"><h1>Directory waitlist</h1><p class="lede">Everyone who asked to be told when consultants open in their area. Stored in our own Vercel KV store, read through a private key only you have.</p></div>
  <div class="panel" id="admin-gate">
    <p class="hint">Enter the admin key you set as <code>ADMIN_SECRET</code> in Vercel (Settings -&gt; Environment Variables). Saved in this browser only.</p>
    <div class="fields" style="display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap;max-width:520px">
      <div class="field" style="flex:1;margin:0"><label for="admin-key">Admin key</label><input id="admin-key" type="password" autocomplete="off"></div>
      <button class="btn btn-primary" id="admin-load" type="button">Load</button>
    </div>
    <p class="field-error" id="admin-error" hidden></p>
  </div>
  <div id="admin-results" hidden>
    <div class="tabs" role="tablist" style="display:flex;gap:6px;margin-bottom:14px">
      <button class="btn btn-ghost btn-sm" type="button" data-list="carrier" aria-selected="true">Carriers</button>
      <button class="btn btn-ghost btn-sm" type="button" data-list="consultant" aria-selected="false">Consultants</button>
    </div>
    <div class="stats" style="margin:0 0 14px"><div><small>Signed up</small><b id="admin-count">0</b></div></div>
    <button class="btn btn-ghost" id="admin-copy" type="button">Copy all emails</button>
    <p class="fine" id="admin-copied" hidden>Copied.</p>
    <div class="table-wrap" style="margin-top:14px"><table><thead><tr><th>Date</th><th>Email</th><th>Name</th><th>Company</th><th>State</th></tr></thead><tbody id="admin-rows"></tbody></table></div>
  </div>
</main>
<script>
(function () {{
  const $ = (s) => document.querySelector(s);
  const keyInput = $('#admin-key');
  let current = 'carrier'; let rows = [];
  try {{ keyInput.value = localStorage.getItem('fc-admin-key') || ''; }} catch (e) {{}}
  function render() {{
    $('#admin-count').textContent = rows.length;
    $('#admin-rows').innerHTML = rows.map(r => `<tr><td>${{r.ts ? new Date(r.ts * 1000).toLocaleDateString('en-US') : ''}}</td><td>${{r.email}}</td><td>${{r.name || '—'}}</td><td>${{r.company || '—'}}</td><td>${{r.state || '—'}}</td></tr>`).join('');
  }}
  async function load(which) {{
    current = which || current;
    const key = keyInput.value.trim(); const err = $('#admin-error'); err.hidden = true;
    if (!key) {{ err.textContent = 'Enter the admin key.'; err.hidden = false; return; }}
    try {{
      const res = await fetch('/api/admin_waitlist?key=' + encodeURIComponent(key) + '&list=' + current);
      const data = await res.json();
      if (!res.ok || data.ok === false) throw new Error(data.error || "Wrong key, or the waitlist store isn't connected yet.");
      try {{ localStorage.setItem('fc-admin-key', key); }} catch (e) {{}}
      rows = (data.rows || []).slice().sort((a, b) => (b.ts || 0) - (a.ts || 0));
      render();
      document.querySelectorAll('[data-list]').forEach(b => b.setAttribute('aria-selected', String(b.dataset.list === current)));
      $('#admin-results').hidden = false;
    }} catch (e2) {{ err.textContent = e2.message; err.hidden = false; }}
  }}
  document.querySelectorAll('[data-list]').forEach(b => b.addEventListener('click', () => load(b.dataset.list)));
  $('#admin-copy').addEventListener('click', async () => {{
    const emails = rows.map(r => r.email).join(', ');
    try {{ await navigator.clipboard.writeText(emails); }} catch (e) {{ const t = document.createElement('textarea'); t.value = emails; document.body.append(t); t.select(); document.execCommand('copy'); t.remove(); }}
    $('#admin-copied').hidden = false;
  }});
  $('#admin-load').addEventListener('click', () => load());
  keyInput.addEventListener('keydown', (e) => {{ if (e.key === 'Enter') load(); }});
  if (keyInput.value) load();
}})();
</script>
</body>
</html>
"""
LAUNCH_PAGES.add(ADMIN_SLUG)
write(ADMIN_SLUG, admin_page)


# ---------- PRIVATE CONSULTANT APPLICATIONS ADMIN (founder only: reads/writes api/admin_consultants.py) ----------
consultants_admin_page = head("FleetCleared Consultant Applications", "Private consultant applications admin.", CONSULTANTS_ADMIN_SLUG).replace(
    '<link rel="canonical" href="https://fleetcleared.com/' + CONSULTANTS_ADMIN_SLUG + '">\n', "") + f"""<div class="preview-banner">Private page. Not linked anywhere on the site and blocked from search engines.</div>
<header class="site-header"><div class="wrap">{LOGO}<span class="hint">Consultant applications</span></div></header>
<main class="wrap">
  <div class="page-head"><h1>Consultant applications</h1><p class="lede">Every submitted listing, screened automatically against the others already on file. Approving one makes it a live listing in <code>consultants:listings</code>; nothing here emails the applicant, since no email sender is wired up yet.</p></div>
  <div class="panel" id="cadmin-gate">
    <p class="hint">Enter the admin key you set as <code>ADMIN_SECRET</code> in Vercel (Settings -&gt; Environment Variables). Saved in this browser only.</p>
    <div class="fields" style="display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap;max-width:520px">
      <div class="field" style="flex:1;margin:0"><label for="cadmin-key">Admin key</label><input id="cadmin-key" type="password" autocomplete="off"></div>
      <button class="btn btn-primary" id="cadmin-load" type="button">Load</button>
    </div>
    <p class="field-error" id="cadmin-error" hidden></p>
  </div>
  <div id="cadmin-results" hidden>
    <div class="tabs" role="tablist" style="display:flex;gap:6px;margin:14px 0">
      <button class="btn btn-ghost btn-sm" type="button" data-status="pending" aria-selected="true">Pending</button>
      <button class="btn btn-ghost btn-sm" type="button" data-status="second_look" aria-selected="false">Second look</button>
      <button class="btn btn-ghost btn-sm" type="button" data-status="approved" aria-selected="false">Approved</button>
      <button class="btn btn-ghost btn-sm" type="button" data-status="rejected" aria-selected="false">Rejected</button>
    </div>
    <div class="stats" style="margin:0 0 14px"><div><small>Showing</small><b id="cadmin-count">0</b></div></div>
    <div id="cadmin-rows" style="display:grid;gap:12px"></div>
  </div>
</main>
<script>
(function () {{
  const $ = (s) => document.querySelector(s);
  const keyInput = $('#cadmin-key');
  let current = 'pending';
  try {{ keyInput.value = localStorage.getItem('fc-admin-key') || ''; }} catch (e) {{}}

  function bandClass(band) {{ return band === 'hold' ? 'band High' : band === 'check' ? 'band Medium' : 'band Low'; }}

  function card(a) {{
    const div = document.createElement('div');
    div.className = 'panel';
    div.style.display = 'grid'; div.style.gap = '8px';
    const reasons = (a.screenReasons || []).map(r => `<li>${{r.reason}} (+${{r.points}})</li>`).join('') || '<li>No warning signs</li>';
    const actions = a.status === 'pending' || a.status === 'second_look'
      ? `<button class="btn btn-primary btn-sm" data-act="approve" data-id="${{a.id}}">Approve</button>
         <button class="btn btn-ghost btn-sm" data-act="reject" data-id="${{a.id}}">Reject</button>
         ${{a.status === 'pending' ? `<button class="btn btn-ghost btn-sm" data-act="second_look" data-id="${{a.id}}">Ask for a second look</button>` : ''}}`
      : '';
    div.innerHTML = `
      <div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap">
        <div><b style="font-size:18px">${{a.name}}</b><div class="hint">${{a.email}} &middot; ${{a.phone}} &middot; ${{a.states}}</div></div>
        <span class="${{bandClass(a.screenBand)}}">${{a.screenBandLabel}} (${{a.screenScore}})</span>
      </div>
      <div class="hint">${{a.description || 'No description given'}}</div>
      <div class="hint">Specialties: ${{a.specialties || '—'}} &middot; Hours: ${{a.hours || '—'}} &middot; Prefers ${{a.contactPref}} &middot; ${{a.timezone}}</div>
      <ul class="hint" style="margin:0;padding-left:18px">${{reasons}}</ul>
      <div style="display:flex;gap:8px;flex-wrap:wrap">${{actions}}</div>
    `;
    div.querySelectorAll('button[data-act]').forEach(b => b.addEventListener('click', () => act(a.id, b.dataset.act)));
    return div;
  }}

  async function load(status) {{
    current = status || current;
    const key = keyInput.value.trim(); const err = $('#cadmin-error'); err.hidden = true;
    if (!key) {{ err.textContent = 'Enter the admin key.'; err.hidden = false; return; }}
    try {{
      const res = await fetch('/api/admin_consultants?key=' + encodeURIComponent(key) + '&status=' + current);
      const data = await res.json();
      if (!res.ok || data.ok === false) throw new Error(data.error || "Wrong key, or the application store isn't connected yet.");
      try {{ localStorage.setItem('fc-admin-key', key); }} catch (e) {{}}
      const rows = (data.rows || []).slice().sort((a, b) => (b.submittedAt || 0) - (a.submittedAt || 0));
      $('#cadmin-count').textContent = rows.length;
      $('#cadmin-rows').replaceChildren(...rows.map(card));
      document.querySelectorAll('[data-status]').forEach(b => b.setAttribute('aria-selected', String(b.dataset.status === current)));
      $('#cadmin-results').hidden = false;
    }} catch (e2) {{ err.textContent = e2.message; err.hidden = false; }}
  }}

  async function act(id, action) {{
    const key = keyInput.value.trim();
    try {{
      const res = await fetch('/api/admin_consultants?key=' + encodeURIComponent(key), {{
        method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify({{ id, action }}),
      }});
      const data = await res.json();
      if (!res.ok || data.ok === false) throw new Error(data.error || 'That action failed.');
      load();
    }} catch (e2) {{ $('#cadmin-error').textContent = e2.message; $('#cadmin-error').hidden = false; }}
  }}

  document.querySelectorAll('[data-status]').forEach(b => b.addEventListener('click', () => load(b.dataset.status)));
  $('#cadmin-load').addEventListener('click', () => load());
  keyInput.addEventListener('keydown', (e) => {{ if (e.key === 'Enter') load(); }});
  if (keyInput.value) load();
}})();
</script>
</body>
</html>
"""
LAUNCH_PAGES.add(CONSULTANTS_ADMIN_SLUG)
write(CONSULTANTS_ADMIN_SLUG, consultants_admin_page)
