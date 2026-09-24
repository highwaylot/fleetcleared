import json, os, pathlib, shutil

# Builds every HTML page of the site. Run from anywhere: python3 tools/build_site.py
ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://fleetcleared.com"
# Two builds from one source:
#   python3 tools/build_site.py                 -> preview: every page, noindex, written into the repo
#   FC_LAUNCH=1 python3 tools/build_site.py     -> public soft launch: guides and tools only, indexable, written to dist/
LAUNCH = os.environ.get("FC_LAUNCH") == "1"
# FC_HOLD_INDEX=1 publishes the launch pages but keeps search engines out, for an interim live site
# before the company details are filled in. Remove it from vercel.json to go fully live.
HOLD_INDEX = os.environ.get("FC_HOLD_INDEX") == "1"
OUT = ROOT / "dist" if LAUNCH else ROOT
LAUNCH_PAGES = {"index.html", "guides.html", "for-consultants.html", "privacy.html", "terms.html", "robots.txt", "sitemap.xml", "site.webmanifest", "favicon.svg"}  # guides are added by build_guides.py
UPDATED = "September 22, 2026"

ICON = {
  "folder": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z"/>',
  "noslash": '<circle cx="12" cy="12" r="8.5"/><line x1="6" y1="18" x2="18" y2="6"/>',
  "search": '<circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16" y2="16"/>',
  "tag": '<path d="M20.6 13.4L11 3.8A2 2 0 0 0 9.6 3.2L4 3l.2 5.6a2 2 0 0 0 .6 1.4l9.6 9.6a2 2 0 0 0 2.8 0l4.4-4.4a2 2 0 0 0 0-2.8z"/><circle cx="8" cy="8" r="1"/>',
  "target": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="1"/>',
  "card": '<rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/>',
  "personcheck": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c0-4 3-6.5 6.5-6.5s6.5 2.5 6.5 6.5"/><path d="M16.5 12.5l1.7 1.7L22 10.5"/>',
  "share": '<circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="6" r="2.5"/><circle cx="18" cy="18" r="2.5"/><line x1="8.3" y1="10.8" x2="15.7" y2="7.2"/><line x1="8.3" y1="13.2" x2="15.7" y2="16.8"/>',
  "lock": '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
  "ban": '<circle cx="12" cy="12" r="8.5"/><line x1="6" y1="6" x2="18" y2="18"/>',
  "trash": '<path d="M4 7h16"/><path d="M9 7V4h6v3"/><path d="M6 7l1 13h10l1-13"/>',
  "scale": '<path d="M12 3v18"/><path d="M5 21h14"/><path d="M4 8h16"/><path d="M4 8l-2 6a3 3 0 0 0 4 0z"/><path d="M20 8l-2 6a3 3 0 0 0 4 0z"/>',
  "cash": '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2.5"/>',
}
def icon(name):
    return f'<span class="icon-badge" aria-hidden="true"><svg viewBox="0 0 24 24">{ICON[name]}</svg></span>'

SPRITE = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
  <defs>
    <linearGradient id="fcGrad" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#17b978"/><stop offset="1" stop-color="#0a5c40"/>
    </linearGradient>
    <symbol id="fc-shield" viewBox="0 0 24 24">
      <g transform="rotate(-16 12 12)">
        <path d="M12 1.6L4.3 4.7v6.1c0 5.2 3.4 8.9 7.7 10.2 4.3-1.3 7.7-5 7.7-10.2V4.7L12 1.6z" fill="url(#fcGrad)"/>
        <line x1="12" y1="5.2" x2="12" y2="9.2" stroke="#fff" stroke-width="1.7" stroke-linecap="round"/>
        <line x1="12" y1="11.8" x2="12" y2="15.8" stroke="#fff" stroke-width="1.7" stroke-linecap="round"/>
      </g>
    </symbol>
  </defs>
</svg>'''

LOGO = '<a class="logo" href="index.html" aria-label="FleetCleared home"><svg aria-hidden="true"><use href="#fc-shield"/></svg><span>Fleet</span><span class="cleared">Cleared</span></a>'

def head(title, desc, path, extra=""):
    # Preview pages are never indexed. Launch pages are.
    robots = "index, follow" if LAUNCH and not HOLD_INDEX else "noindex, nofollow"
    url = f"{SITE}/{path}" if path else f"{SITE}/"
    return f'''<!DOCTYPE html>
<html lang="en"{' data-directory="off"' if LAUNCH else ''}>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#0f4c3a">
<link rel="icon" href="favicon.ico" sizes="32x32">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="assets/icons/apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<meta property="og:type" content="website">
<meta property="og:site_name" content="FleetCleared">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@600;700&family=Public+Sans:wght@400;600;700&display=swap">
<link rel="stylesheet" href="assets/site.css">{extra}
</head>
<body>
{SPRITE}
'''

def header(current):
    def a(href, label, key, cls=""):
        cur = ' aria-current="page"' if key == current else ""
        c = f' class="{cls}"' if cls else ""
        return f'<a href="{href}"{c}{cur}>{label}</a>'
    if LAUNCH:
        nav = f'''{a("guides.html", "Guides", "guides")}
      {a("mcs-150-due-date.html", "MCS-150 due date", "mcs")}
      {a("for-consultants.html", "For consultants", "consultants")}
      {a("audit-readiness-check.html", "Audit check", "check", "btn btn-ghost")}'''
        return f'''<header class="site-header">
  <div class="wrap">
    {LOGO}
    <nav class="site-nav" aria-label="Main">
      {nav}
    </nav>
  </div>
</header>
'''
    return f'''<header class="site-header">
  <div class="wrap">
    {LOGO}
    <nav class="site-nav" aria-label="Main">
      {a("browse.html", "Find a consultant", "browse")}
      {a("guides.html", "Guides", "guides")}
      {a("for-consultants.html", "For consultants", "list", "btn btn-ghost")}
    </nav>
  </div>
</header>
'''

FOOTER = f'''<footer class="site-footer">
  <div class="wrap">
    <div>
      {LOGO}
      <p class="footer-note">A directory that connects trucking companies with independent DOT compliance consultants. We don't perform, certify, or guarantee compliance work.</p>
    </div>
    <ul class="footer-links">
      <li><a href="browse.html">Find a consultant</a></li>
      <li><a href="privacy.html">Privacy policy</a></li>
      <li><a href="for-consultants.html">For consultants</a></li>
      <li><a href="terms.html">Terms of service</a></li>
      <li><a href="guides.html">Guides &amp; free tools</a></li>
    </ul>
    <p class="footer-legal">© 2026 FleetCleared. Not affiliated with the FMCSA or the U.S. Department of Transportation.</p>
  </div>
</footer>
<script src="assets/rules.js"></script>
<script src="assets/hours.js"></script>
<script src="assets/site.js" defer></script>
</body>
</html>
'''
# Vercel Web Analytics: cookieless, aggregate page-view counts. No-ops until you enable it once
# in Vercel's dashboard (Project -> Analytics -> Enable). Disclosed in the launch privacy policy.
ANALYTICS = '<script defer src="/_vercel/insights/script.js"></script>' if LAUNCH else ''
if LAUNCH:
    FOOTER = f'''<footer class="site-footer">
  <div class="wrap">
    <div>
      {LOGO}
      <p class="footer-note">Plain-language DOT compliance guides and free tools for small trucking companies. General information, not legal advice. A directory of independent compliance consultants is coming in 2027.</p>
    </div>
    <ul class="footer-links">
      <li><a href="guides.html">Guides &amp; free tools</a></li>
      <li><a href="for-consultants.html">For consultants</a></li>
      <li><a href="privacy.html">Privacy policy</a></li>
      <li><a href="mcs-150-due-date.html">MCS-150 due date</a></li>
      <li><a href="terms.html">Terms of use</a></li>
    </ul>
    <p class="footer-legal">© 2026 FleetCleared. Not affiliated with the FMCSA or the U.S. Department of Transportation.</p>
  </div>
</footer>
{ANALYTICS}
</body>
</html>
'''

PAGES = {}
def write(name, html):
    PAGES[name] = html
    if LAUNCH and name not in LAUNCH_PAGES:
        return
    (OUT / name).parent.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(html)

# ---------- HOME ----------
ld = {
  "@context": "https://schema.org",
  "@graph": [
    {"@type": "Organization", "@id": f"{SITE}/#org", "name": "FleetCleared", "url": f"{SITE}/", "logo": f"{SITE}/assets/icons/icon-512.png"},
    {"@type": "WebSite", "@id": f"{SITE}/#site", "name": "FleetCleared", "url": f"{SITE}/", "publisher": {"@id": f"{SITE}/#org"}},
  ],
}
write("index.html", head(
  "FleetCleared — Find a DOT Compliance Consultant",
  "Find an independent DOT compliance consultant for your trucking company. Free to search and connect.",
  "", extra=f'\n<script type="application/ld+json">{json.dumps(ld)}</script>') + header("home") + f'''<main>
  <section class="hero wrap">
    <span class="eyebrow">Free to search &amp; connect</span>
    <h1>Find a DOT compliance consultant before a bad inspection finds you.</h1>
    <p class="lede">Hours of service, driver files, drug and alcohol testing, maintenance records. One missed requirement can cost you your operating authority. FleetCleared connects you with independent compliance consultants near you, at no cost to you. Consultants set their own rates.</p>
    <p class="no-robocalls"><strong>No robocalls. No surprise emails.</strong> Nobody contacts you unless you ask them to.</p>
    <div class="hero-actions">
      <a class="btn btn-primary btn-lg" href="browse.html">Find a consultant</a>
      <a class="btn btn-ghost btn-lg" href="for-consultants.html">List your practice</a>
    </div>
  </section>
  <ul class="trust-strip">
    <li>{icon("folder")}<span><strong>Directory only</strong> — we don't perform compliance work</span></li>
    <li>{icon("noslash")}<span><strong>No guarantees</strong> — we don't certify or verify outcomes</span></li>
    <li>{icon("search")}<span><strong>Your call</strong> — always do your own due diligence</span></li>
  </ul>
</main>
''' + FOOTER)


MODAL = """<div class="modal-backdrop" id="contact-modal" hidden>
  <div class="modal" role="dialog" aria-modal="true" aria-labelledby="contact-title">
    <div class="modal-head">
      <div>
        <h2 id="contact-title">Request contact</h2>
        <p>Sending to <strong id="contact-to"></strong></p>
      </div>
      <button class="icon-btn" type="button" data-close aria-label="Close">&times;</button>
    </div>
    <form id="contact-form">
      <div class="field"><label for="cf-name">Your name</label><input id="cf-name" required autocomplete="name"></div>
      <div class="field"><label for="cf-co">Company name</label><input id="cf-co" autocomplete="organization"></div>
      <div class="field"><label for="cf-fleet">How many trucks do you run?</label><select id="cf-fleet" required><option value="">Choose one</option><option value="1">1 truck</option><option value="2">2 trucks</option><option value="3">3–10 trucks</option><option value="11">11 or more</option></select></div>
      <fieldset class="field choice">
        <legend>How should they reach you?</legend>
        <div class="segmented">
          <label><input type="radio" name="cf-via" id="cf-via-call" value="call" checked><span>Call</span></label>
          <label><input type="radio" name="cf-via" id="cf-via-text" value="text"><span>Text</span></label>
          <label><input type="radio" name="cf-via" id="cf-via-email" value="email"><span>Email</span></label>
        </div>
        <p class="hint" id="cf-pref-note"></p>
        <p class="hint consent" id="cf-text-consent" hidden>By choosing Text, you agree that <span class="cf-to-name"></span> may text you about this request. Message and data rates may apply.</p>
      </fieldset>
      <div class="field"><label for="cf-contact" id="cf-contact-label">Phone number</label><input id="cf-contact" required type="tel" autocomplete="tel" aria-describedby="cf-contact-error"><span class="field-error" id="cf-contact-error" hidden></span></div>
      <p class="hint remembered" id="cf-remembered" hidden>We filled in your details from last time. <button type="button" class="link-btn" id="cf-forget">Clear them</button></p>
      <div class="field"><label for="cf-need">What do you need help with? <span class="hint">(optional)</span></label><textarea id="cf-need" rows="2" placeholder="Example: new entrant audit next month"></textarea></div>
      <div class="modal-actions">
        <button type="button" class="btn btn-ghost" data-close>Cancel</button>
        <button type="submit" class="btn btn-primary">Send request</button>
      </div>
      <p class="fine">We share what you enter here with this consultant only. By sending, you agree to our <a href="terms.html">terms</a> and <a href="privacy.html">privacy policy</a>.</p>
    </form>
    <p class="notice" id="contact-done" hidden>Request sent. The consultant will contact you directly. After you've talked, we'll email you a link to leave a review.</p>
  </div>
</div>"""

# ---------- BROWSE ----------
states = ["AL","AR","FL","GA","IN","KS","KY","MO","NE","NJ","NM","NY","OH","OK","PA","TX"]
specs = ["Audits","CSA Scores","DQ Files","Drug & Alcohol","New Entrant Audits","Owner-Operators","Bilingual"]
write("browse.html", head(
  "Find a DOT Compliance Consultant | FleetCleared",
  "Browse independent DOT and FMCSA compliance consultants by state and specialty. Free for carriers.",
  "browse.html") + header("browse") + f'''<main class="wrap">
  <div class="page-head">
    <h1>Find a compliance consultant</h1>
    <p class="lede">Filter by the state you run in and what you need help with. Requesting contact is free. The consultant reaches out to you directly.</p>
  </div>
  <div class="filters">
    <select id="f-state" aria-label="State"><option value="">All states</option>{"".join(f"<option>{s}</option>" for s in states)}</select>
    <select id="f-spec" aria-label="Specialty"><option value="">All specialties</option>{"".join(f"<option>{s.replace('&','&amp;')}</option>" for s in specs)}</select>
    <input id="f-q" type="search" placeholder="Search by company name" aria-label="Search by company name">
    <select id="f-sort" aria-label="Sort"><option value="rating">Top rated</option><option value="reviews">Most reviews</option><option value="name">Name A–Z</option></select>
    <label class="check-inline" for="f-open"><input id="f-open" type="checkbox"> Taking requests now</label>
    <button class="btn btn-ghost btn-sm" type="button" id="f-clear" hidden>Clear filters</button>
  </div>
  <p class="result-count" id="result-count" aria-live="polite"></p>
  <div class="grid" id="grid"></div>
  <p class="empty" id="empty" hidden>No consultants match those filters yet. Try another state or clear the specialty.</p>
  <section class="launch-empty" id="empty-launch" hidden>
    <h2>We're adding consultants now</h2>
    <p>FleetCleared is new, and we're reaching out to compliance consultants state by state. Listings will show up here as each one is approved.</p>
    <p>Are you a consultant? Listing is free, and your first lead is on us.</p>
    <p><a class="btn btn-primary" href="for-consultants.html">List your practice</a></p>
  </section>
</main>

{MODAL}
''' + FOOTER)


# ---------- CONSULTANT PROFILE (one page, rendered from #slug) ----------
write("consultant.html", head(
  "Consultant Profile | FleetCleared",
  "Services, service area, contact hours, and reviews from carriers who contacted this compliance consultant through FleetCleared.",
  "consultant.html") + header("browse") + f"""<main>
  <section class="wrap launch-empty" id="profile-missing" hidden style="padding-top:48px">
    <h2>This listing isn't available</h2>
    <p>It may have been removed, or the link is incomplete.</p>
    <p><a class="btn btn-primary" href="browse.html">Find a consultant</a></p>
  </section>
  <div id="profile-page">
  <div class="wrap back-row"><a class="back-link" href="browse.html">← Back to results</a></div>
  <section class="profile-top">
    <div class="cover" aria-hidden="true"></div>
    <div class="wrap profile-head">
      <div class="org-logo profile-logo" id="p-logo" aria-hidden="true"></div>
      <div class="profile-id">
        <h1 id="p-name">Consultant</h1>
        <p class="profile-meta"><span id="p-region"></span> · <a href="#reviews" class="rating-link" id="p-rating-link"></a></p>
        <p class="open-chip" id="p-open-chip"></p>
      </div>
      <div class="profile-actions">
        <button class="btn btn-primary btn-lg" type="button" id="p-contact">Request contact</button>
      </div>
    </div>
    <div class="wrap" id="p-limit" hidden><p class="limit-note">This consultant has reached the number of new requests they take each month. They'll be taking requests again on <strong id="p-limit-date"></strong>. Other consultants in your state may be available now.</p></div>
    <nav class="wrap profile-tabs" role="tablist" aria-label="Profile sections">
      <button role="tab" type="button" id="tab-about" aria-selected="true" aria-controls="about">About</button>
      <button role="tab" type="button" id="tab-reviews" aria-selected="false" aria-controls="reviews">Reviews <span class="count" id="p-review-count"></span></button>
    </nav>
  </section>

  <div class="wrap profile-body">
    <aside class="intro">
      <section class="panel">
        <h2>Contact details</h2>
        <dl class="facts-list">
          <div><dt>Prefers</dt><dd><span class="pref-chip" id="p-pref"></span></dd></div>
          <div><dt>Usually responds</dt><dd id="p-response"></dd></div>
          <div><dt>Languages</dt><dd id="p-langs"></dd></div>
          <div><dt>In business since</dt><dd id="p-since"></dd></div>
        </dl>
        <p class="hint">Contact details are shared after you send a request, so every request is tracked and answered.</p>
      </section>
      <section class="panel">
        <h2>Hours to contact</h2>
        <p class="open-line" id="p-open-line"></p>
        <p class="hint" id="p-tz"></p>
        <table class="hours"><tbody id="p-hours"></tbody></table>
      </section>
    </aside>

    <div class="profile-main">
      <section id="about" role="tabpanel" aria-labelledby="tab-about">
        <section class="panel">
          <h2>About</h2>
          <p id="p-about"></p>
        </section>
        <section class="panel">
          <h2>Services</h2>
          <div class="tags" id="p-tags"></div>
        </section>
        <section class="panel">
          <h2>States served</h2>
          <div class="tags" id="p-states"></div>
        </section>
        <p class="disclaimer-line">{icon("folder")}<span>FleetCleared lists this consultant but doesn't verify their credentials or guarantee their work. Ask about experience and get the price in writing.</span></p>
      </section>

      <section id="reviews" role="tabpanel" aria-labelledby="tab-reviews" hidden>
        <section class="panel rating-summary">
          <div class="rating-big"><b id="p-avg"></b><span class="stars" id="p-avg-stars"></span><span class="hint" id="p-total"></span></div>
          <div class="bars" id="p-bars"></div>
        </section>
        <p class="sample-flag">Sample reviews for the design preview. Real reviews appear only after launch.</p>
        <div class="review-tools"><label for="p-review-sort">Sort reviews</label><select id="p-review-sort"><option value="newest">Newest first</option><option value="lowest">Lowest rated first</option><option value="highest">Highest rated first</option></select></div>
        <div id="p-review-list" class="review-list"></div>
        <section class="panel how-reviews">
          <h2>How reviews work</h2>
          <ul class="review-rules">
            <li>Only carriers who contacted this consultant through FleetCleared can review them.</li>
            <li>Because reviews affect real businesses, every reviewer's identity is confirmed before a review is posted, with a one-time code and their USDOT number.</li>
            <li>Posting a false review breaks our <a href="terms.html#reviews">terms</a>.</li>
            <li>We never remove a review for being negative, and consultants can't pay to change reviews.</li>
          </ul>
        </section>
      </section>
    </div>
  </div>
  </div>
  <div class="mobile-bar" id="p-mobile-bar"><div><b id="p-mobile-name"></b><span id="p-mobile-open"></span></div><span id="p-mobile-btn"></span></div>
</main>

{MODAL}
""" + FOOTER)

# ---------- FOR CONSULTANTS ----------
write("for-consultants.html", head(
  "List Your Compliance Practice | FleetCleared",
  "DOT compliance consultants: list your practice free and get contacted by trucking companies in your states. Your first lead is free.",
  "for-consultants.html") + header("list") + f'''<main class="wrap">
  <div class="page-head">
    <span class="eyebrow">For compliance consultants</span>
    <h1>List your practice. Get found by carriers who need you.</h1>
    <p class="lede">Listing is free. You pay only when a trucking company sends you its contact details, and your first one is on us.</p>
  </div>
  <ul class="facts">
    <li>{icon("tag")}<strong>Free to list</strong>No listing fee and no subscription.</li>
    <li>{icon("target")}<strong>First lead free</strong>Your first real carrier contact costs nothing.</li>
    <li>{icon("card")}<strong>Pay per lead after</strong>Add a card once your free lead is used.</li>
    <li>{icon("personcheck")}<strong>Reviewed by a person</strong>Every listing is checked by hand, usually within 1–2 business days.</li>
  </ul>
  <section class="pricing" aria-labelledby="pricing-title">
    <h2 id="pricing-title">What a lead costs</h2>
    <p>You pay only when a carrier sends you their contact details. The price depends on the size of their fleet, because bigger fleets are bigger clients. Leads go to you alone and are never sold to another consultant.</p>
    <div class="table-wrap"><table><thead><tr><th>Carrier's fleet</th><th>Price per lead</th></tr></thead><tbody id="price-rows"></tbody></table></div>
    <p class="hint">Your first lead is free. Set a monthly limit so you're never surprised. Fake or duplicate requests are credited back.</p>
    <div class="estimator" id="estimator">
      <h3>Estimate your month</h3>
      <div class="est-grid">
        <div class="field"><label for="est-leads">Requests you might get</label><input id="est-leads" type="range" min="0" max="30" value="6"><span class="hint"><b id="est-leads-out">6</b> a month</span></div>
        <div class="field"><label for="est-fleet">Typical carrier</label><select id="est-fleet"><option value="1">1–2 trucks</option><option value="3" selected>3–10 trucks</option><option value="11">11+ trucks</option></select></div>
        <div class="field"><label for="est-cap">Your monthly limit</label><select id="est-cap"><option value="5">5 leads</option><option value="10" selected>10 leads</option><option value="20">20 leads</option><option value="">No limit</option></select></div>
      </div>
      <p class="est-result" id="est-result" aria-live="polite"></p>
    </div>
  </section>
  <div class="signup-layout">
  <div class="form-card">
    <h2>Submit your listing</h2>
    <p>We'll email you once it's approved. <span class="hint" id="lf-draft-note" hidden>Draft saved on this device.</span></p>
    <form id="list-form">
      <input type="checkbox" name="botcheck" class="hp-field" tabindex="-1" autocomplete="off">
      <div class="form-grid">
        <div class="field"><label for="lf-name">Company name</label><input id="lf-name" required autocomplete="organization"></div>
        <div class="field"><label for="lf-email">Work email</label><input id="lf-email" type="email" required autocomplete="email"><span class="hint">A company email address speeds up approval.</span></div>
        <div class="field"><label for="lf-phone">Phone</label><input id="lf-phone" type="tel" required autocomplete="tel"></div>
        <div class="field"><label for="lf-states">States you serve</label><input id="lf-states" required placeholder="OH, IN, KY"></div>
        <div class="field"><label for="lf-pref">Best way to reach you</label><select id="lf-pref"><option value="call">Phone call</option><option value="text">Text message</option><option value="email">Email</option></select></div>
        <div class="field"><label for="lf-tz">Time zone</label><select id="lf-tz"><option>Eastern</option><option selected>Central</option><option>Mountain</option><option>Pacific</option><option>Alaska</option><option>Hawaii</option></select></div>
        <div class="field full"><label for="lf-cap">Monthly lead limit</label><select id="lf-cap"><option value="5">Up to 5 leads a month</option><option value="10" selected>Up to 10 leads a month</option><option value="20">Up to 20 leads a month</option><option value="">No limit</option></select><span class="hint">Once you reach it, new requests are politely declined until next month. You can change it any time.</span></div>
        <div class="field full"><label for="lf-hours">Hours carriers can contact you</label><input id="lf-hours" placeholder="Mon–Fri 7 AM – 5 PM, Sat 8 AM – noon"><span class="hint">Shown on your profile so carriers know when to expect a reply.</span></div>
        <div class="field full"><label for="lf-spec">Specialties</label><input id="lf-spec" placeholder="DQ files, HOS audits, drug and alcohol programs"></div>
        <div class="field full"><label for="lf-desc">Short description</label><textarea id="lf-desc" rows="3" maxlength="300" placeholder="Which carriers do you help, and with what?"></textarea><span class="hint"><span id="lf-desc-count">0</span> / 300</span></div>
        <div class="field full">
          <label for="lf-logo">Company logo <span class="hint">(optional)</span></label>
          <div class="logo-upload">
            <div class="org-logo placeholder" id="logo-preview" aria-hidden="true">?</div>
            <div><input id="lf-logo" type="file" accept="image/png,image/jpeg,image/webp"><p class="hint">Upload only a logo you own or have permission to use. Square images work best. Until you add one, we show your initials.</p></div>
          </div>
        </div>
      </div>
      <label class="agree" for="lf-agree"><input id="lf-agree" type="checkbox" required><span>I agree to the <a href="terms.html">terms of service</a>, including per-lead billing after my first free lead, and I've read the <a href="privacy.html">privacy policy</a>.</span></label>
      <p class="field-error" id="lf-error" hidden></p>
      <button class="btn btn-primary btn-lg btn-block" type="submit">Submit for review</button>
    </form>
    <p class="notice" id="list-done" hidden>Your listing is in the review queue. We'll email you once it's approved.</p>
  </div>
  <aside class="listing-preview" aria-label="Preview of your listing">
    <p class="preview-label">How carriers will see you</p>
    <article class="card">
      <div class="card-id">
        <div class="org-logo placeholder" id="pv-logo" aria-hidden="true">?</div>
        <div><h2 id="pv-name">Your company</h2><p class="region" id="pv-meta">Your states · No reviews yet</p></div>
      </div>
      <p class="desc" id="pv-desc">Your short description shows here.</p>
      <div class="tags" id="pv-tags"></div>
      <p class="hint" id="pv-pref"></p>
    </article>
  </aside>
  </div>
</main>
''' + FOOTER)


# ---------- APPLICATION STATUS (linked from the review email only) ----------
write("application-status.html", head(
  "Application Status | FleetCleared", "Check the status of your FleetCleared listing application.", "application-status.html") + header(None) + f"""<main class="wrap">
  <div class="page-head">
    <span class="eyebrow">Listing application</span>
    <h1>Your listing needs a closer look</h1>
    <p class="lede">Thanks for applying. Before we approve a listing, we confirm it belongs to a real business that isn't already listed. We couldn't confirm everything yet.</p>
  </div>
  <div class="status-grid">
    <section class="panel">
      <h2>What we couldn't confirm</h2>
      <ul class="check-list">
        <li><span class="dot warn" aria-hidden="true"></span>Some contact details match a business already listed on FleetCleared.</li>
        <li><span class="dot warn" aria-hidden="true"></span>Your email address isn't on a company domain.</li>
        <li><span class="dot ok" aria-hidden="true"></span>Business registration found.</li>
      </ul>
      <p class="hint">This isn't a judgment of your qualifications. It's how we keep one listing per business.</p>
    </section>
    <section class="panel">
      <h2>Ask for a second look</h2>
      <form id="appeal-form">
        <div class="field"><label for="ap-why">Tell us what we should know</label><textarea id="ap-why" rows="4" required placeholder="Example: we share an office with another consultant, and we're a separate company."></textarea></div>
        <div class="field"><label for="ap-link">Website or state business filing <span class="hint">(optional)</span></label><input id="ap-link" type="url" placeholder="https://"></div>
        <button class="btn btn-primary btn-block" type="submit">Send for a second look</button>
      </form>
      <p class="notice" id="appeal-done" hidden>Sent. A person will review your application, usually within 2 business days, and email you either way.</p>
    </section>
  </div>
</main>
""" + FOOTER)

# ---------- LEGAL ----------
DRAFT = '<p class="draft-flag"><strong>Draft for review.</strong> Highlighted items are placeholders to fill in, and this page should be reviewed by a lawyer before launch.</p>'
def fill(t): return f'<span class="fill">{t}</span>'

def legal_page(fname, title, desc, h1, lede, summary_items, sections):
    toc = "".join(f'<li><a href="#{sid}">{st}</a></li>' for sid, st, _ in sections)
    body = "".join(f'<h2 id="{sid}">{st}</h2>{html}' for sid, st, html in sections)
    summ = "".join(f"<li>{icon(i)}<span>{t}</span></li>" for i, t in summary_items)
    write(fname, head(title, desc, fname) + header(None) + f'''<main class="wrap">
  <div class="page-head">
    <h1>{h1}</h1>
    <p class="lede">{lede}</p>
    {DRAFT}
  </div>
  <div class="legal">
    <nav class="legal-toc" aria-label="On this page"><p>On this page</p><ol>{toc}</ol></nav>
    <article class="legal-body">
      <section class="summary"><h2>The short version</h2><ul>{summ}</ul></section>
      {body}
    </article>
  </div>
</main>
''' + FOOTER)

ENTITY = fill("[FleetCleared LLC]")
STATE = fill("[State]")
legal_page("privacy.html", "Privacy Policy | FleetCleared",
  "How FleetCleared collects, uses, and shares information from trucking companies and compliance consultants.",
  "Privacy policy", f"Last updated {UPDATED}. This policy explains what we collect when you use fleetcleared.com and what we do with it.",
  [("share", "When you request contact, we send your name and contact details to <strong>the one consultant you chose</strong>. Nobody else."),
   ("ban", "We <strong>never sell</strong> your information and we don't run advertising trackers."),
   ("lock", "Card payments go through Stripe. <strong>We never see or store card numbers.</strong>"),
   ("trash", "You can ask us to see, correct, or delete your information at any time.")],
  [
   ("who", "Who we are", f"<p>FleetCleared is operated by {ENTITY} (\"FleetCleared,\" \"we,\" \"us\"). FleetCleared is a directory. We connect trucking companies with independent DOT compliance consultants. We are not a compliance consultant, and we are not affiliated with the FMCSA or the U.S. Department of Transportation.</p>"),
   ("collect", "What we collect", """<h3>If you're a trucking company</h3><p>When you use \"Request contact,\" we collect your name, company name, fleet size, phone number or email address, how you'd like to be contacted, and anything you write about what you need help with. Browsing the directory does not require an account.</p><h3>If you sign up for deadline reminders</h3><p>We collect your email address and, if you want texts, your mobile number and your agreement to receive them, the deadlines you picked, and your USDOT number if you give it. We use these only to send the reminders you asked for. We never pass them to consultants. Reply STOP to any text or use the unsubscribe link in any email to stop, and we'll delete your details on request. The free tools work on your device: nothing you type into them is sent to us.</p>
<h3>If you're a consultant</h3><p>When you apply to list your practice, we collect your company name, work email, phone number, the states you serve, your specialties, your description, and your logo if you upload one. If you add a payment method, our payment processor, Stripe, collects your card details directly.</p>
<h3>If you write a review</h3><p>To confirm you're a real customer, we collect a one-time code sent to your email or phone and your company's USDOT number, which we check against public FMCSA records. Your rating and review text are public, shown with your first name, last initial, and company type (for example \"Owner-operator\"). Your contact details and USDOT number are never shown.</p>
<h3>Collected automatically</h3><p>Like most websites, our hosting provider records basic technical information when you visit, such as IP address, browser type, and pages requested. We use it to keep the site running and to prevent abuse. We use only the cookies needed for the site to work. We don't use advertising or cross-site tracking cookies.</p>"""),
   ("use", "How we use it", """<ul><li>To send your contact request to the consultant you chose.</li><li>To review consultant applications, including checks that catch spam and duplicate accounts. We compare email domains, phone numbers, business addresses, IP addresses, and a card identifier provided by Stripe (not the card number) against existing accounts, and may check whether a phone number is a mobile, landline, or internet line and whether a business is registered with its state.</li><li>To price leads, using the fleet size a carrier reports, which we may compare with public FMCSA records.</li><li>To keep a record of each contact request, which is how we bill consultants and resolve billing questions.</li><li>To confirm the identity of people who write reviews.</li><li>To email you about your request, listing, or account, including a link to review the consultant you contacted. We don't send marketing texts.</li><li>To keep the site secure and meet our legal obligations.</li></ul>"""),
   ("share", "Who we share it with", """<ul><li><strong>The consultant you contact.</strong> Your request goes to that one consultant, by the contact method you chose. If you choose text, you're agreeing that this consultant may text you about your request. If that consultant can't take your request, we tell you. We never pass it to a different consultant without your permission. Once a consultant has your request, their own privacy practices apply to how they use it.</li><li><strong>Service providers</strong> that run parts of FleetCleared for us, such as hosting, email delivery, payments (Stripe), and phone-number verification. They may use the information only to provide their service to us.</li><li><strong>Google Fonts.</strong> Our pages load fonts from Google, which receives your IP address when the font files load.</li><li><strong>Legal reasons.</strong> If the law requires it, or to protect people's rights and safety.</li><li><strong>Business transfer.</strong> If FleetCleared is sold or merged, this information may transfer to the new owner under this policy.</li></ul><p>We do not sell personal information, and we do not share it for cross-context behavioral advertising.</p>"""),
   ("keep", "How long we keep it", f"<p>We keep contact-request records for {fill('[24 months]')} so we can handle billing questions, then delete or anonymize them. Consultant listing information stays while the listing is active and for {fill('[12 months]')} after it closes. We may keep some records longer where the law requires it.</p>"),
   ("rights", "Your choices and rights", "<p>You can ask to see, correct, or delete the personal information we hold about you, or ask for a copy of it. Depending on where you live, including California and other U.S. states with privacy laws, you may have additional rights, and you won't be treated differently for using them. Email <strong>privacy@fleetcleared.com</strong> and we'll respond within 45 days. We may need to confirm your identity first.</p><p>If a consultant already received your request, ask them directly to delete their copy too.</p>"),
   ("security", "Security", "<p>We use reasonable safeguards, including encrypted connections and limited staff access, to protect your information. No system is perfectly secure, so we can't guarantee absolute security.</p>"),
   ("kids", "Children", "<p>FleetCleared is for businesses. It isn't directed to anyone under 18, and we don't knowingly collect information from children.</p>"),
   ("changes", "Changes to this policy", "<p>If we make a material change, we'll update the date at the top and, where appropriate, email affected consultants before it takes effect.</p>"),
   ("contact", "Contact us", f"<p>Questions about privacy: <strong>privacy@fleetcleared.com</strong><br>Mail: {ENTITY}, {fill('[mailing address]')}</p>"),
  ])

legal_page("terms.html", "Terms of Service | FleetCleared",
  "The terms that apply to trucking companies and compliance consultants using FleetCleared.",
  "Terms of service", f"Last updated {UPDATED}. These terms are an agreement between you and {ENTITY}. By using fleetcleared.com, you agree to them.",
  [("folder", "FleetCleared is a <strong>directory only</strong>. We don't give compliance advice, and we don't vouch for any consultant."),
   ("personcheck", "Our listing review screens for spam and duplicate accounts. It <strong>does not check a consultant's qualifications</strong>."),
   ("cash", "Carriers use FleetCleared free. Consultants <strong>pay per lead after one free lead</strong>. Any work between you is a deal between you."),
   ("scale", "If something goes wrong between a carrier and a consultant, it's between them. Our liability is limited, as explained below.")],
  [
   ("service", "What FleetCleared is", "<p>FleetCleared lists independent DOT and FMCSA compliance consultants so trucking companies can find and contact them. We are not a party to any agreement between a carrier and a consultant. We do not perform, supervise, certify, verify, or guarantee any consultant's work, credentials, or results, and nothing on the site is legal or compliance advice. FleetCleared is not affiliated with the FMCSA or the U.S. Department of Transportation.</p><p>Appearing on FleetCleared is not an endorsement. We review listings by hand to screen out spam, fake businesses, and duplicate accounts. That review does not assess a consultant's expertise, licensing, or quality of work.</p>"),
   ("eligibility", "Who can use it", "<p>You must be at least 18 and using FleetCleared for business purposes. If you use it on behalf of a company, you confirm you're authorized to accept these terms for that company.</p><p>Consultants accept these terms by checking the \"I agree\" box when they apply. Carriers accept them by sending a contact request, submitting a review, or signing up for reminders. Reading a guide or using a free tool is subject to these terms too.</p>"),
   ("carriers", "For trucking companies", "<ul><li>Searching the directory and requesting contact are free.</li><li>Give accurate contact information, and only submit a request when you actually want the consultant to contact you.</li><li>Evaluate any consultant yourself before you hire them. Check references, ask about experience, and get the scope and price in writing.</li><li>Any fees for a consultant's services are set by that consultant and paid to them, not to FleetCleared.</li></ul>"),
   ("consultants", "For consultants", "<ul><li>Keep your listing accurate and up to date. Don't claim credentials, affiliations, or results you can't back up.</li><li>Don't suggest you are, or work for, a government agency. That includes business names, logos, or wording that imply you are the DOT, the FMCSA, or an official filing service. We may reject or remove listings that do.</li><li>Don't contact carriers who haven't sent you a request through FleetCleared using information from the site.</li><li>One listing per business. Creating extra accounts to get additional free leads is prohibited. We may close those accounts and charge for leads they received.</li><li>Use a carrier's contact details only to respond to that carrier's request. Don't sell, share, or add them to marketing lists.</li><li>You are solely responsible for the services and advice you provide, including following all laws and professional obligations that apply to you.</li><li>You grant FleetCleared permission to display your listing content and logo on the site for as long as your listing is active.</li></ul>"),
   ("leads", "Leads, pricing, and payment", f"""<p>A <strong>lead</strong> is a contact request that a carrier submits through your listing with a name and a phone number or email address. Page views and clicks are never leads.</p>
<ul><li>Each approved business receives one free lead. Accounts that share a phone number, business address, payment card, or company email domain are treated as one business and share that one free lead.</li><li><strong>Lead prices</strong> depend on the fleet size the carrier reports: {fill('[$30]')} for 1–2 trucks, {fill('[$45]')} for 3–10 trucks, and {fill('[$65]')} for 11 or more. We may check a carrier's fleet size against public FMCSA records.</li><li><strong>Monthly limit.</strong> You choose a monthly lead limit. Once you reach it, we tell new carriers you're unavailable until next month, and you're not charged for those requests.</li><li>After that, you need a payment method on file to receive more leads.</li><li><strong>Payment authorization.</strong> When you add a payment method, you authorize FleetCleared to charge it automatically for each lead delivered to you, at the per-lead price shown in your account at the time of delivery. We email a receipt for every charge. We'll give at least {fill('[30 days]')} notice by email before changing the price, and you can remove your payment method at any time to stop receiving paid leads.</li><li><strong>If no payment method is on file</strong>, we hold a new request for up to {fill('[48 hours]')} and email you to add one. If you don't, we tell the carrier you're unavailable so they can contact someone else. We never send their request to another consultant without their permission.</li><li>Payments are processed by Stripe under Stripe's terms.</li><li>If a lead is clearly invalid (for example, fake contact details or a duplicate of a lead you already received), tell us within {fill('[14 days]')} and we'll review it. We credit leads we confirm are invalid. A carrier deciding not to hire you does not make a lead invalid.</li><li>If a carrier chooses to be contacted by text, you may text them about their request only. Don't add them to marketing texts or lists.</li></ul>"""),
   ("reviews", "Reviews", f"""<p>Reviews affect real businesses, so we confirm who every reviewer is before a review is published.</p>
<ul><li><strong>Who can review.</strong> Only a carrier that sent a contact request to that consultant through FleetCleared. We email a private review link to the address or phone number used in that request.</li><li><strong>How we confirm identity.</strong> The reviewer enters a one-time code sent to that email or phone, plus their company's USDOT number, which we check against public FMCSA records. The USDOT number is never shown publicly.</li><li><strong>What a review must be.</strong> Your own real experience with that consultant. No reviews you were paid or rewarded for, no reviews of your own business or a competitor, no threats, and no personal information about anyone.</li><li><strong>Submitting a false review is a violation of these terms.</strong> We may remove it, close the reviewer's access, and share what we know with the business affected or with authorities where the law allows or requires.</li></ul>
<p><strong>What we don't do.</strong> We never remove, hide, or reorder a review because it's negative, and consultants can't pay to change reviews. We remove a review only when it breaks the rules above or the law requires it. Consultants may post one public reply to each review, and may ask us to check a review against these rules. By posting a review, you let us display it on FleetCleared.</p>"""),
   ("copyright", "Copyright complaints", f"<p>Consultants may upload only logos and content they own or have permission to use. If you believe something on FleetCleared infringes your copyright, send a notice to our designated agent at <strong>copyright@fleetcleared.com</strong> ({ENTITY}, {fill('[mailing address]')}) that includes: your contact information, the work you believe is infringed, where the material appears on FleetCleared, a statement that you have a good-faith belief the use isn't authorized, a statement under penalty of perjury that your notice is accurate and you're authorized to act, and your signature. We remove material covered by a valid notice and close the accounts of repeat infringers. If your material was removed and you believe that was a mistake, you can send a counter-notice to the same address.</p>"),
   ("guides", "Guides, free tools and reminders", "<p>Our guides, the MCS-150 due-date tool, the audit readiness check and deadline reminders are general information for convenience. They are not legal or compliance advice, they don't create any professional relationship with FleetCleared or with any consultant who reviewed a guide, and they may be incomplete or out of date when rules change. Don't rely on them in place of the official regulations, FMCSA's own records and notices, or a qualified professional.</p><p>Tool results are estimates from the information you enter. The readiness check is a self-check, not an audit result, and answering \"yes\" to every question doesn't mean you'll pass an audit. Always confirm deadlines in your FMCSA registration and with the agency that sets them.</p><p>Reminders are a free courtesy. We don't guarantee that any reminder will be sent, arrive, or arrive on time, and you remain responsible for meeting every deadline whether or not you get a reminder. You can stop reminders at any time.</p><p>When a listed consultant reviews a guide, their name shows they checked it for accuracy. It isn't advice from that consultant to you, and it isn't an endorsement of that consultant by FleetCleared. If you spot an error, tell us at <strong>corrections@fleetcleared.com</strong> and we'll review it.</p>"),
   ("conduct", "Things you can't do", "<ul><li>Submit false information or impersonate anyone.</li><li>Scrape, copy, or bulk-download listings or contact details.</li><li>Send spam, or use the site to harass anyone.</li><li>Interfere with the site's security or operation.</li></ul>"),
   ("applications", "Listing applications and second looks", "<p>We review every listing application by hand. To protect carriers and prevent duplicate accounts, we check details such as your phone number, business address, email domain, and business registration, and compare them with existing accounts. These checks screen for spam and duplicates. They don't judge your qualifications.</p><p>If we need a closer look, we'll tell you in general terms what we couldn't confirm and ask for more information. You can ask for a second look at any time by replying with details that help, such as your business registration, website, or an explanation (for example, a shared office). A person reviews every request, usually within 2 business days.</p>"),
   ("ending", "Suspending or closing accounts", "<p>We may decline, suspend, or remove a listing that breaks these terms or puts carriers at risk. You can close your listing at any time by emailing us. Charges for leads already delivered remain due.</p>"),
   ("disclaimers", "Disclaimers", "<p>FleetCleared is provided \"as is\" and \"as available.\" To the fullest extent the law allows, we disclaim all warranties, express or implied, including warranties about any consultant, the accuracy of listings or guides, the results of any tool, the delivery of any reminder, or the results of any compliance work.</p>"),
   ("liability", "Limitation of liability", f"<p>To the fullest extent the law allows, FleetCleared is not liable for indirect, incidental, special, consequential, or punitive damages, or for lost profits, fines, penalties, or loss of operating authority, arising from your use of the site, our guides, tools or reminders, or from any consultant's services. Our total liability for any claim is limited to the greater of the amount you paid FleetCleared in the 12 months before the claim or {fill('[$100]')}.</p>"),
   ("indemnity", "Indemnity", "<p>If you're a consultant, you agree to defend and indemnify FleetCleared against claims arising from your services, your listing content, or your breach of these terms.</p>"),
   ("law", "Governing law and disputes", f"<p>These terms are governed by the laws of {STATE}, without regard to conflict-of-law rules. Disputes will be resolved in the state or federal courts located in {fill('[County, State]')}, unless we both agree otherwise.</p>"),
   ("changes", "Changes to these terms", "<p>We may update these terms. If a change is material, we'll update the date at the top and notify listed consultants by email before it takes effect. Continuing to use FleetCleared after that means you accept the updated terms.</p>"),
   ("contact", "Contact", f"<p><strong>legal@fleetcleared.com</strong><br>{ENTITY}, {fill('[mailing address]')}</p>"),
  ])

# ---------- ADMIN (not linked from public pages, always noindex) ----------
admin_head = head("FleetCleared Admin", "Internal admin.", "admin.html").replace(
  '<link rel="canonical" href="https://fleetcleared.com/admin.html">\n', "")
write("admin.html", admin_head + f"""<div class="preview-banner">Design preview. On the live site this page requires sign-in and is never linked from public pages.</div>
<header class="site-header"><div class="wrap">{LOGO}<span class="hint">Signed in as founder@fleetcleared.com</span></div></header>
<main class="wrap" style="padding-block:32px 64px">
  <div class="page-head" style="padding-block:0 24px"><h1>Admin</h1><p class="lede">Every new listing is approved by hand. The screening score only tells you where to look harder.</p></div>
  <div class="stats">
    <div class="stat"><b id="stat-pending">–</b><span>Waiting for review</span></div>
    <div class="stat"><b id="stat-appeals">–</b><span>Asked for a second look</span></div>
    <div class="stat"><b id="stat-leads">–</b><span>Leads, last 30 days</span></div>
    <div class="stat"><b id="stat-revenue">–</b><span>Charged, last 30 days</span></div>
  </div>
  <div class="tabs" role="tablist">
    <button role="tab" type="button" aria-selected="true" aria-controls="panel-pending">Waiting for review</button>
    <button role="tab" type="button" aria-selected="false" aria-controls="panel-appeals">Second-look requests</button>
    <button role="tab" type="button" aria-selected="false" aria-controls="panel-listings">Active listings</button>
    <button role="tab" type="button" aria-selected="false" aria-controls="panel-leads">Lead log</button>
  </div>
  <section id="panel-pending" role="tabpanel">
    <div class="table-wrap"><table><thead><tr><th>Company</th><th>Email</th><th>Submitted</th><th>Screening</th><th>Why</th><th></th></tr></thead><tbody id="pending-rows"></tbody></table></div>
    <p class="admin-note">Clear 0–24 · Check 25–59 · Hold 60+ (contact the applicant before deciding). Scores are signals for you, never automatic rejections. "No free lead" means this business already used its free lead under another account.</p>
  </section>
  <section id="panel-appeals" role="tabpanel" hidden>
    <div id="appeal-list" class="appeal-list"></div>
  </section>
  <section id="panel-listings" role="tabpanel" hidden>
    <div class="table-wrap"><table><thead><tr><th>Company</th><th>States</th><th>Free lead</th><th>Card on file</th><th>This month</th><th>Leads</th></tr></thead><tbody>
      <tr><td>Buckeye Fleet Advisors</td><td>OH, IN, KY</td><td><span class="pill pill-trial">Used Sep 10</span></td><td><span class="pill pill-ok">Yes</span></td><td>4 of 10</td><td>Receiving</td></tr>
      <tr><td>Red Mesa Compliance</td><td>TX, OK, NM</td><td><span class="pill pill-trial">Not used</span></td><td><span class="pill pill-warn">No</span></td><td>0, no limit</td><td>Receiving</td></tr>
      <tr><td>Delta Pine Safety Co.</td><td>GA, FL, AL</td><td><span class="pill pill-trial">Used Sep 18</span></td><td><span class="pill pill-warn">No</span></td><td>1 of 5</td><td><strong>Held until card added</strong></td></tr>
    </tbody></table></div>
  </section>
  <section id="panel-leads" role="tabpanel" hidden>
    <div class="table-wrap"><table><thead><tr><th>Date</th><th>Consultant</th><th>Carrier contact</th><th>Trucks</th><th>Result</th><th>Charged</th></tr></thead><tbody id="lead-rows"></tbody></table></div>
    <p class="admin-note">Only a submitted name plus phone or email counts as a lead. The price comes from the carrier's fleet size: 1–2 trucks $30, 3–10 $45, 11+ $65.</p>
  </section>
</main>
<script src="assets/rules.js"></script>
<script src="assets/admin.js" defer></script>
</body>
</html>
""")


# ---------- GUIDES AND FREE TOOLS ----------
exec(open(pathlib.Path(__file__).with_name("build_guides.py")).read())


# ---------- TASTE OF FLEETCLEARED (demo copy in /demo, fictional data) ----------
DEMO = ROOT / "demo"
if not LAUNCH: DEMO.mkdir(exist_ok=True)
def demo_write(name, html):
    if not LAUNCH: (DEMO / name).write_text(html)
BANNER = '<div class="demo-banner">Taste of FleetCleared: every business and review here is fictional. <a href="index.html">Back to the tour</a></div>\n'
def demo_copy(html):
    for a, b in [('"assets/', '"../assets/'), ('"favicon', '"../favicon'), ('"site.webmanifest"', '"../site.webmanifest"'),
                 ('href="terms.html', 'href="../terms.html'), ('href="privacy.html', 'href="../privacy.html')]:
        html = html.replace(a, b)
    html = html.replace('<meta name="robots"', '<meta name="robots"', 1)
    html = html.replace('<script src="../assets/rules.js"></script>', '<script src="../assets/rules.js"></script>\n<script src="../assets/demo-data.js"></script>', 1)
    body = html.index('</svg>', html.index('<body>')) + len('</svg>\n')
    return html[:body] + BANNER + html[body:]
for name in ["browse.html", "consultant.html", "for-consultants.html"]:
    demo_write(name, demo_copy(PAGES[name]))
demo_write("application-status.html", demo_copy(PAGES["application-status.html"].replace(
    "Thanks for applying. Before we approve", "Thanks for applying, Summit Lane Safety. Before we approve")))

tour_consultants = [
  ("red-mesa-compliance", "Top rated", "Red Mesa Compliance", "Five-star reviews, prefers text, uploaded logo, bilingual."),
  ("buckeye-fleet-advisors", "Solid, with a reply", "Buckeye Fleet Advisors", "Strong rating, one mixed review, and the consultant's public reply."),
  ("delta-pine-safety", "Mixed rating", "Delta Pine Safety Co.", "Prefers email and responds slower. A 2-star review sits next to a 4-star."),
  ("two-rivers-compliance", "Low rated", "Two Rivers Compliance", "Bad reviews stay up. We never remove a review for being negative."),
  ("keystone-haul-safety", "Monthly limit reached", "Keystone Haul Safety", "The consultant capped their leads. Carriers see when they'll be available again."),
  ("prairie-line-carrier-services", "Brand new", "Prairie Line Carrier Services", "No reviews and no logo yet, so the placeholder logo shows their initials."),
]
cards = "".join(f'<a class="tour-card" href="consultant.html#{slug}"><span class="variation">{v}</span><b>{n}</b><span>{d}</span></a>' for slug, v, n, d in tour_consultants)
tour = head("Taste of FleetCleared", "A walkthrough of FleetCleared with fictional example listings.", "demo/") + header(None) + f"""<main class="wrap">
  <div class="page-head">
    <span class="eyebrow">Taste of FleetCleared</span>
    <h1>See how FleetCleared works before you list</h1>
    <p class="lede">Everything below uses fictional businesses and reviews, so you can click through exactly what carriers and consultants see.</p>
  </div>
  <div class="tour">
    <section class="tour-section">
      <h2>What carriers see</h2>
      <p>Carriers search by state and specialty, open a profile, and send one request to one consultant. Nothing is shared with anyone else.</p>
      <div class="tour-grid"><a class="tour-card" href="browse.html"><span class="variation">Search</span><b>Find a consultant</b><span>Filter by state and specialty, then open a profile.</span></a>{cards}</div>
    </section>
    <section class="tour-section">
      <h2>What consultants see</h2>
      <p>Listing is free and your first lead is on us. After that you pay per lead, by fleet size, with a monthly limit you choose.</p>
      <div class="tour-grid">
        <a class="tour-card" href="for-consultants.html"><span class="variation">Pricing and signup</span><b>List your practice</b><span>Lead prices, your monthly limit, and the signup form.</span></a>
        <a class="tour-card" href="application-status.html"><span class="variation">Application review</span><b>Asked for a closer look</b><span>What happens when we can't confirm something, and how to ask for a second look.</span></a>
      </div>
    </section>
  </div>
</main>
""" + FOOTER
demo_write("index.html", demo_copy(tour).replace(BANNER, '<div class="demo-banner">Taste of FleetCleared: every business and review here is fictional.</div>\n'))


# ---------- REVIEW HUB (founder only: never linked, never indexed) ----------
import subprocess, html as _html
log = subprocess.run(["git", "-C", str(ROOT), "log", "--format=%h|%ad|%s", "--date=format:%b %-d, %-I:%M %p"], capture_output=True, text=True).stdout.strip().splitlines()
log_rows = "".join(f'<tr><td>{_html.escape(d)}</td><td>{_html.escape(m)}</td><td><code>{h}</code></td></tr>' for h, d, m in (l.split("|", 2) for l in log))
def rlink(href, title, note):
    return f'<a class="tour-card" href="{href}"><b>{title}</b><span>{note}</span></a>'
review_page = head("FleetCleared Review", "Founder review hub.", "review.html").replace('<link rel="canonical" href="https://fleetcleared.com/review.html">\n', "") + f"""<div class="preview-banner">Founder review page. Not linked from the site and blocked from search engines. Remove or protect it before launch.</div>
<header class="site-header"><div class="wrap">{LOGO}<span class="hint">Review hub</span></div></header>
<main class="wrap">
  <div class="page-head"><h1>Review every piece in one place</h1><p class="lede">The live site starts empty. The example consultants live only in the demo, so you can see how each situation looks and works without anything going live.</p></div>
  <div class="tour">
    <section class="tour-section"><h2>Live site (what launches)</h2><p>No listings yet. This is exactly what the public will see on day one.</p>
      <div class="tour-grid">{rlink("index.html","Home","No-robocalls message, trust strip")}{rlink("browse.html","Find a consultant","Empty state: we're adding consultants now")}{rlink("for-consultants.html","For consultants","Pricing table, monthly limit, signup")}{rlink("application-status.html","Application status","Flagged applicant and second-look request")}{rlink("terms.html","Terms of service","Draft for lawyer review")}{rlink("privacy.html","Privacy policy","Draft for lawyer review")}</div></section>
    <section class="tour-section"><h2>Example consultants (demo only)</h2><p>Fictional data from <code>assets/demo-data.js</code>. Each one shows a different situation.</p>
      <div class="tour-grid">{rlink("demo/index.html","Demo tour","The walkthrough page to show consultants")}{rlink("demo/browse.html","Demo search","All six examples, with filters")}{rlink("demo/consultant.html#red-mesa-compliance","Top rated","Red Mesa Compliance")}{rlink("demo/consultant.html#buckeye-fleet-advisors","Solid, with a reply","Buckeye Fleet Advisors")}{rlink("demo/consultant.html#delta-pine-safety","Mixed rating","Delta Pine Safety Co.")}{rlink("demo/consultant.html#two-rivers-compliance","Low rated","Two Rivers Compliance")}{rlink("demo/consultant.html#keystone-haul-safety","Monthly limit reached","Keystone Haul Safety")}{rlink("demo/consultant.html#prairie-line-carrier-services","Brand new","Prairie Line Carrier Services")}</div></section>
    <section class="tour-section"><h2>How the code decides</h2><p>Pricing and screening live in <code>assets/rules.js</code>, checked by <code>tests/rules.test.js</code> (run <code>npm test</code>). The admin preview is a separate private link.</p></section>
    <section class="tour-section"><h2>Iteration log</h2><p>Every saved version, newest first. Each code is a commit you can go back to.</p>
      <div class="table-wrap"><table><thead><tr><th>When</th><th>What changed</th><th>Version</th></tr></thead><tbody>{log_rows}</tbody></table></div></section>
  </div>
</main>
<script src="assets/rules.js"></script>
</body>
</html>
"""
write("review.html", review_page)

# ---------- PUBLIC SOFT LAUNCH (home, terms, privacy for a site that collects nothing) ----------
if LAUNCH:
    exec(open(pathlib.Path(__file__).with_name("build_launch.py")).read())

# ---------- SEO / platform files ----------
if LAUNCH and HOLD_INDEX:
    write("robots.txt", "# Interim live site: hidden from search engines until the company details are filled in.\nUser-agent: *\nDisallow: /\n")
    pages = ["", "guides.html", "for-consultants.html"] + [p for p in GUIDE_PAGES if p != "guides.html"] + ["privacy.html", "terms.html"]
elif LAUNCH:
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    pages = ["", "guides.html", "for-consultants.html"] + [p for p in GUIDE_PAGES if p != "guides.html"] + ["privacy.html", "terms.html"]
else:
    write("robots.txt", "# PREVIEW MODE: blocks all crawlers. The public build (FC_LAUNCH=1) writes its own.\nUser-agent: *\nDisallow: /\n")
    pages = ["", "browse.html", "for-consultants.html", "privacy.html", "terms.html"] + GUIDE_PAGES
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      "".join(f"  <url><loc>{SITE}/{p}</loc><lastmod>{GUIDES_ISO}</lastmod></url>\n" for p in pages) + "</urlset>\n")
write("site.webmanifest", json.dumps({
  "name": "FleetCleared", "short_name": "FleetCleared", "start_url": "/", "display": "browser",
  "background_color": "#f4f6f4", "theme_color": "#0f4c3a",
  "icons": [{"src": "/assets/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "/assets/icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}, indent=2) + "\n")
write("favicon.svg", '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
  <defs><linearGradient id="g" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#17b978"/><stop offset="1" stop-color="#0a5c40"/></linearGradient></defs>
  <g transform="rotate(-16 12 12)">
    <path d="M12 1.6L4.3 4.7v6.1c0 5.2 3.4 8.9 7.7 10.2 4.3-1.3 7.7-5 7.7-10.2V4.7L12 1.6z" fill="url(#g)"/>
    <line x1="12" y1="5.2" x2="12" y2="9.2" stroke="#fff" stroke-width="1.9" stroke-linecap="round"/>
    <line x1="12" y1="11.8" x2="12" y2="15.8" stroke="#fff" stroke-width="1.9" stroke-linecap="round"/>
  </g>
</svg>
''')
if LAUNCH:
    # Static files the public pages use. Nothing private (admin, demo data, rules) is copied.
    for f in ["assets/site.css", "assets/deadlines.js", "assets/guides.js", "assets/og-image.png", "favicon.ico"]:
        (OUT / f).parent.mkdir(parents=True, exist_ok=True); shutil.copy(ROOT / f, OUT / f)
    shutil.copytree(ROOT / "assets/icons", OUT / "assets/icons", dirs_exist_ok=True)
    # Refuse to call the build ready while any placeholder or preview-only link remains.
    problems = []
    for f in sorted(OUT.rglob("*.html")):
        t = f.read_text()
        for needle, why in [('class="fill"', "unfilled placeholder"), *([] if HOLD_INDEX else [("noindex", "noindex tag")]), ("draft-flag", "draft note"),
                            ('href="browse.html', "link to the directory"),
                            ("review-pending", "review-pending label"), ('id="remind-form"', "reminder form")]:
            if needle in t: problems.append(f"{f.relative_to(OUT)}: {why}")
    # FC_PREVIEW_BLANKS=1 lets a private preview show blank company details; nothing else is allowed through.
    if problems and (os.environ.get("FC_PREVIEW_BLANKS") == "1" or HOLD_INDEX) and all(p.endswith("unfilled placeholder") for p in problems):
        print("PRIVATE PREVIEW ONLY, not publishable:\n  " + "\n  ".join(problems))
    elif problems:
        print("NOT READY TO PUBLISH:\n  " + "\n  ".join(problems)); raise SystemExit(1)
    print(f"ok: public build in {OUT.relative_to(ROOT)}/ ({len(list(OUT.rglob('*.html')))} pages)")
else:
    print("ok")
