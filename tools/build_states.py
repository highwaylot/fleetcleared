# Per-state SEO landing pages ("DOT compliance consultants in <State>"). Run through build_site.py.
# Liability rule: the ONLY state-specific claim on these pages is the name/link of the official state
# motor-carrier agency, sourced straight from that agency's own .gov site. We never restate a state's
# specific permit/authority rules ourselves -- that's the kind of claim that's expensive to keep accurate
# across 50 states and creates real liability if it's wrong or goes stale. Point to the source instead.

def state_slug(name):
    return "dot-compliance-consultants-" + name.lower().replace(" ", "-") + ".html"

STATE_PAGES = []  # slugs, filled below

# abbr -> (agency_name, agency_url, note_or_None). note is an optional short caveat shown under the
# agency box (e.g. when two agencies split the duty, or we could only confidently verify the agency
# name and not the exact current URL).
STATE_AGENCY = {}

def state_cta(name, abbr):
    if LAUNCH:
        return f'''<aside class="guide-cta">
  <h2>Want someone to handle this in {name}?</h2>
  <p>An independent DOT compliance consultant can check your records and do this work for you. Our consultant directory opens in 2027. Until then, look for someone with safety audit experience and ask for references.</p>
  <a class="btn btn-primary" href="index.html#waitlist">Get first pick when we open</a>
</aside>'''
    return f'''<aside class="guide-cta">
  <h2>Want someone to handle this in {name}?</h2>
  <p>Independent DOT compliance consultants on FleetCleared do this work for small carriers every day. Free to search, and nobody contacts you unless you ask.</p>
  <a class="btn btn-primary" href="browse.html?state={abbr}">Find a consultant in {name}</a>
</aside>'''

STATE_RELATED = ["guide-new-entrant-safety-audit.html", "guide-drug-alcohol-consortium.html", "guide-compliance-calendar.html"]

def state_page(abbr, name):
    agency_name, agency_url, note = STATE_AGENCY[abbr]
    slug = state_slug(name)
    STATE_PAGES.append(slug)
    LAUNCH_PAGES.add(slug)
    title = f"DOT Compliance Consultants in {name} | FleetCleared"
    desc = f"Find an independent DOT compliance consultant for your trucking company in {name}. Free to search. Plus where to find {name}'s own official motor carrier requirements."
    h1 = f"DOT compliance consultants in {name}"
    answer = f"FleetCleared is a free directory connecting small trucking companies in {name} with independent DOT/FMCSA compliance consultants. We don't perform, certify or guarantee compliance work &mdash; for {name}'s own current requirements, go straight to {agency_name}, linked below."
    toc_sections = [
      ("need", f"Do you need a compliance consultant in {name}?"),
      ("authority", f"Interstate vs. intrastate authority in {name}"),
      ("directory", "What FleetCleared does"),
    ]
    toc = "".join(f'<li><a href="#{i}">{h}</a></li>' for i, h in toc_sections)
    body = f'''<h2 id="need">Do you need a compliance consultant in {name}?</h2>
<p>Most small carriers manage compliance themselves until something makes it harder to keep up: a new entrant safety audit, a CSA warning letter, driver files that have fallen behind, or simply not enough hours in the day. An independent DOT compliance consultant can review your records, help you prepare for an audit, or run your drug and alcohol program for you. It's optional, and plenty of carriers in {name} never need one.</p>
<h2 id="authority">Interstate vs. intrastate authority in {name}</h2>
<p>If you operate across state lines, you're regulated primarily by FMCSA under your USDOT number: new entrant safety audits, hours of service, drug and alcohol testing and the rest of 49 CFR apply the same way in every state. If you operate only within {name}, you may also need separate state operating authority or permits on top of that. Exactly what's required, and how it's changed recently, is {name}'s call to make &mdash; not ours.</p>
<div class="panel">
  {icon("scale")}
  <h3>{name}'s own source</h3>
  <p><a href="{agency_url}" rel="noopener">{agency_name}</a> is the official state agency for motor carrier regulation in {name}. Confirm any state-specific registration, permit or intrastate authority requirement directly with them before you rely on it.{f" {note}" if note else ""}</p>
</div>
<h2 id="directory">What FleetCleared does</h2>
<p>We're a directory, not a regulator and not a law firm. Listing is free for carriers, one lead is free, and nobody contacts you unless you ask them to. We never certify, vouch for, or guarantee any consultant's compliance work, in {name} or anywhere else.</p>'''
    srcs = f'<li><a href="{agency_url}" rel="noopener">{agency_name} ({name})</a></li>' + "".join(f'<li><a href="{u}" rel="noopener">{l}</a></li>' for l, u in [FMCSA_FAQ, ECFR_NE])
    rel = "".join(f'<a class="tour-card" href="{s}"><span class="variation">{g}</span><b>{c}</b><span>{b}</span></a>'
                  for s, c, b, g in RELATED_INDEX if s in STATE_RELATED)
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Article", "headline": h1, "description": desc, "dateModified": GUIDES_ISO, "datePublished": GUIDES_ISO,
             "mainEntityOfPage": f"{SITE}/{slug}", "publisher": {"@id": f"{SITE}/#org"}, "author": {"@type": "Organization", "@id": f"{SITE}/#org", "name": "FleetCleared"}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "States", "item": f"{SITE}/states.html"},
                {"@type": "ListItem", "position": 2, "name": name, "item": f"{SITE}/{slug}"}]},
        ],
    }
    extra = f'\n<script type="application/ld+json">{json.dumps(ld)}</script>'
    write(slug, head(title, desc, slug, extra) + header("guides") + f'''<main class="wrap">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="states.html">States</a> <span aria-hidden="true">/</span> <span>{name}</span></nav>
  <div class="page-head guide-head">
    <h1>{h1}</h1>
    <div class="short-answer"><span class="eyebrow">Short answer</span><p>{answer}</p></div>
    <p class="guide-meta">Updated {GUIDES_UPDATED}</p>
    <p class="guide-notice">General information, not legal advice. Rules change: check the linked sources or a qualified consultant before acting. <a href="terms.html#guides">How to use our guides</a></p>
  </div>
  <div class="legal guide">
    <aside class="legal-toc"><p>On this page</p><ol>{toc}<li><a href="#sources">Sources</a></li></ol></aside>
    <article class="legal-body">
{body}
      {state_cta(name, abbr)}
      <h2 id="sources">Sources</h2>
      <ul class="sources">{srcs}</ul>
      {DISCLAIMER}
    </article>
  </div>
  <section class="related"><h2>Keep reading</h2><div class="tour-grid">{rel}</div></section>
</main>
''' + guide_scripts(""))

for abbr, name in US_STATES:
    if abbr in STATE_AGENCY:
        state_page(abbr, name)

# ---------------------------------------------------------------- hub
covered = [name for abbr, name in US_STATES if abbr in STATE_AGENCY]
states_ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "DOT compliance consultants by state", "url": f"{SITE}/states.html", "publisher": {"@id": f"{SITE}/#org"}}
state_cards = "".join(
    f'<a class="tour-card" href="{state_slug(name)}"><span class="variation">{abbr}</span><b>{name}</b><span>Where to find {name}\'s own requirements, and a free consultant search.</span></a>'
    for abbr, name in US_STATES if abbr in STATE_AGENCY)
LAUNCH_PAGES.add("states.html")
write("states.html", head("DOT Compliance Consultants by State | FleetCleared",
  "Find an independent DOT compliance consultant in your state, plus a direct link to your state's own official motor carrier agency.",
  "states.html", f'\n<script type="application/ld+json">{json.dumps(states_ld)}</script>') + header("guides") + f'''<main class="wrap">
  <div class="page-head">
    <span class="eyebrow">By state</span>
    <h1>Find a compliance consultant in your state</h1>
    <p class="lede">Every state page links straight to that state's own official motor carrier agency, plus a free consultant search. {len(covered)} states covered so far.</p>
  </div>
  <div class="tour-grid">{state_cards}</div>
  {DISCLAIMER}
</main>
''' + FOOTER)
