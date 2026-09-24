# Public soft launch pages: home, terms of use and privacy for a site that collects no personal information.
# Run through tools/build_site.py with FC_LAUNCH=1. Values come from tools/launch.json; empty ones render as
# placeholders, and the build refuses to finish until they're filled.

CFG = json.loads((pathlib.Path(__file__).with_name("launch.json")).read_text())
def cfg(key):
    v = str(CFG.get(key, "")).strip()
    return v if v else fill(f"[{key.replace('_', ' ')}]")
NAME, FORMED, ADDRESS, COURTS, CAP, EFFECTIVE = (cfg(k) for k in ["legal_name", "state_of_formation", "mailing_address", "court_county_and_state", "liability_cap_dollars", "effective_date"])
# Blank web3forms_key just hides the waitlist section; it never blocks the build (unlike the fields above).
WEB3FORMS_KEY = str(CFG.get("web3forms_key", "")).strip()

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
home_cards = "".join(f'<a class="tour-card" href="{s}"><span class="variation">{g}</span><b>{c}</b><span>{b}</span></a>' for s, c, b, g in RELATED_INDEX)
WAITLIST = f'''<section class="form-card wait-card" id="waitlist" aria-labelledby="wait-h">
  <h2 id="wait-h">Get first pick when we open</h2>
  <p>We\'ll email you once when consultants are live in your area. That\'s the only email you\'ll get from this list.</p>
  <form id="waitlist-form" novalidate>
    <input type="hidden" name="access_key" value="{WEB3FORMS_KEY}">
    <input type="hidden" name="subject" value="FleetCleared waitlist signup">
    <input type="checkbox" name="botcheck" class="hp-field" tabindex="-1" autocomplete="off">
    <div class="field"><label for="wl-email">Email</label><input id="wl-email" name="email" type="email" autocomplete="email" required></div>
    <div class="field"><label for="wl-name">Name (optional)</label><input id="wl-name" name="name" type="text" autocomplete="name"></div>
    <input type="hidden" name="state" id="wl-state" value="">
    <p class="field-error" id="wait-error" hidden></p>
    <button class="btn btn-primary" type="submit">Notify me</button>
  </form>
  <p class="notice" id="wait-done" hidden>You\'re on the list.</p>
  <p class="fine">We only use this to tell you the directory opened. See our <a href="privacy.html">privacy policy</a>.</p>
</section>''' if WEB3FORMS_KEY else ""
write("index.html", head("FleetCleared: Plain-Language DOT Compliance Guides for Small Trucking Companies",
  "Free guides and tools for small trucking companies: the new entrant safety audit, drug and alcohol testing, CSA warning letters and filing deadlines. Sources on every page.",
  "", f'''\n<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@graph": [
    {"@type": "Organization", "@id": f"{SITE}/#org", "name": "FleetCleared", "url": f"{SITE}/", "logo": f"{SITE}/assets/icons/icon-512.png"},
    {"@type": "WebSite", "@id": f"{SITE}/#site", "name": "FleetCleared", "url": f"{SITE}/", "publisher": {"@id": f"{SITE}/#org"}}]})}</script>''') + header(None) + f'''<main>
  <section class="hero wrap">
    <span class="eyebrow">Free guides &amp; tools</span>
    <h1>Plain answers for small carriers facing an audit, a warning letter or a deadline.</h1>
    <p class="lede">What the rules require, what fails a safety audit, and when things are due, in plain words with the official source linked on every page. Free, and no sign-up.</p>
    <p class="no-robocalls"><strong>No robocalls. No sign-up. No sales calls.</strong> We never ask for your phone number.</p>
    <div class="hero-actions">
      <a class="btn btn-primary btn-lg" href="guides.html">Read the guides</a>
      <a class="btn btn-ghost btn-lg" href="audit-readiness-check.html">Take the audit check</a>
    </div>
  </section>
  <ul class="trust-strip">
    <li>{icon("search")}<span><strong>Sources linked</strong> on every page</span></li>
    <li>{icon("noslash")}<span><strong>Not legal advice</strong>: general information</span></li>
    <li>{icon("folder")}<span><strong>Not affiliated</strong> with FMCSA or U.S. DOT</span></li>
  </ul>
  <section class="wrap launch-guides"><div class="tour-grid">{home_cards}</div>
    <p class="fine">A directory of independent DOT compliance consultants is coming in 2027.</p></section>
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
   ("waitlist", "If you sign up to be notified", "<p>If you enter your email (and optionally your name) to be notified when the consultant directory opens, we use it only to send that one announcement, and to see which states people are asking from so we know where to launch next. We use Web3Forms, a third-party form service, to deliver the signup to us; they process it only to send it to us and don't use it for their own marketing. We don't sell it, and we don't pass it to consultants. Email <strong>privacy@fleetcleared.com</strong> to be removed at any time.</p>"),
   ("rights", "Your rights", "<p>Depending on where you live, you may have the right to ask what personal information we hold about you and to have it deleted. Since we don't collect it through the site, there's usually nothing to find, but email <strong>privacy@fleetcleared.com</strong> and we'll check within 45 days.</p>"),
   ("kids", "Children", "<p>FleetCleared is for businesses and isn't directed to anyone under 18.</p>"),
   ("contact", "Contact", f"<p><strong>privacy@fleetcleared.com</strong><br>{NAME}, {ADDRESS}</p>"),
  ])


# ---------- PRIVATE STATUS PAGE (founder only: unguessable URL, never linked, noindex) ----------
# Change STATUS_SLUG any time you want a new private URL; the old one just stops working.
STATUS_SLUG = "status-3b3500e3.html"
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
  </div>
</main>
"""
LAUNCH_PAGES.add(STATUS_SLUG)
write(STATUS_SLUG, status_page)
