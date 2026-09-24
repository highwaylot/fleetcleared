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
  <form id="waitlist-form" novalidate>
    <input type="checkbox" name="botcheck" class="hp-field" tabindex="-1" autocomplete="off">
    <div class="field"><label for="wl-email">Email</label><input id="wl-email" name="email" type="email" autocomplete="email" required></div>
    <div class="field"><label for="wl-name">Name (optional)</label><input id="wl-name" name="name" type="text" autocomplete="name"></div>
    <input type="hidden" name="state" id="wl-state" value="">
    <p class="field-error" id="wait-error" hidden></p>
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
  </section>
  <section class="wrap">{WAITLIST}</section>
</main>
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


# ---------- PRIVATE STATUS PAGE (founder only: unguessable URL, never linked, noindex) ----------
# Change STATUS_SLUG any time you want a new private URL; the old one just stops working.
STATUS_SLUG = "status-3b3500e3.html"
ADMIN_SLUG = "waitlist-7f2c9a1d.html"  # defined here so the status page below can link to it
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
    <div class="stats" style="margin:20px 0"><div><small>Signed up</small><b id="admin-count">0</b></div></div>
    <button class="btn btn-ghost" id="admin-copy" type="button">Copy all emails</button>
    <p class="fine" id="admin-copied" hidden>Copied.</p>
    <div class="table-wrap" style="margin-top:14px"><table><thead><tr><th>Date</th><th>Email</th><th>Name</th><th>State</th></tr></thead><tbody id="admin-rows"></tbody></table></div>
  </div>
</main>
<script>
(function () {{
  const $ = (s) => document.querySelector(s);
  const keyInput = $('#admin-key');
  try {{ keyInput.value = localStorage.getItem('fc-admin-key') || ''; }} catch (e) {{}}
  async function load() {{
    const key = keyInput.value.trim(); const err = $('#admin-error'); err.hidden = true;
    if (!key) {{ err.textContent = 'Enter the admin key.'; err.hidden = false; return; }}
    try {{
      const res = await fetch('/api/admin_waitlist?key=' + encodeURIComponent(key));
      const data = await res.json();
      if (!res.ok || data.ok === false) throw new Error(data.error || 'Wrong key, or the waitlist store isn\\'t connected yet.');
      try {{ localStorage.setItem('fc-admin-key', key); }} catch (e) {{}}
      const rows = (data.rows || []).slice().sort((a, b) => (b.ts || 0) - (a.ts || 0));
      $('#admin-count').textContent = rows.length;
      $('#admin-rows').innerHTML = rows.map(r => `<tr><td>${{r.ts ? new Date(r.ts * 1000).toLocaleDateString('en-US') : ''}}</td><td>${{r.email}}</td><td>${{r.name || '—'}}</td><td>${{r.state || '—'}}</td></tr>`).join('');
      $('#admin-copy').onclick = async () => {{
        const emails = rows.map(r => r.email).join(', ');
        try {{ await navigator.clipboard.writeText(emails); }} catch (e) {{ const t = document.createElement('textarea'); t.value = emails; document.body.append(t); t.select(); document.execCommand('copy'); t.remove(); }}
        $('#admin-copied').hidden = false;
      }};
      $('#admin-results').hidden = false;
    }} catch (e2) {{ err.textContent = e2.message; err.hidden = false; }}
  }}
  $('#admin-load').addEventListener('click', load);
  keyInput.addEventListener('keydown', (e) => {{ if (e.key === 'Enter') load(); }});
  if (keyInput.value) load();
}})();
</script>
</body>
</html>
"""
LAUNCH_PAGES.add(ADMIN_SLUG)
write(ADMIN_SLUG, admin_page)
