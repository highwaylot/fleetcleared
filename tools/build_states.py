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
# Researched via web search (this build environment's egress proxy blocks live .gov fetches, so these
# were cross-referenced across multiple independent, recently-dated search results rather than a live
# HTTP check). Spot-check links before FC_HOLD_INDEX is removed and these become indexable.
STATE_AGENCY = {
  "AL": ("Alabama Public Service Commission – Motor Carrier Section", "https://psc.alabama.gov/motor-carrier-section/",
         "IRP/IFTA registration is handled separately by the Alabama Department of Revenue, Motor Vehicle Division."),
  "AK": ("Alaska Division of Motor Vehicles", "https://dmv.alaska.gov/vehicle-services/commercial-vehicle-registration/",
         "Alaska does not participate in IRP; commercial carriers use dual registration or trip permits."),
  "AZ": ("Arizona Department of Transportation, Motor Vehicle Division – Motor Carrier Services", "https://azdot.gov/mvd/businesses-organizations/motor-carrier-services", None),
  "AR": ("Arkansas Department of Finance and Administration – Motor Carrier / Trucking Portal", "https://www.dfa.arkansas.gov/office/trucking-portal/",
         "Oversize/overweight permits and roadside enforcement are handled by the Arkansas Highway Police (part of ARDOT)."),
  "CA": ("California Department of Motor Vehicles – Motor Carrier Permits", "https://www.dmv.ca.gov/portal/vehicle-industry-services/motor-carrier-services-mcs/motor-carrier-permits/",
         "The CHP's Motor Carrier Safety Unit issues the required CA Carrier Identification Number and regulates safety; the DMV then issues the Motor Carrier Permit itself."),
  "CO": ("Colorado Department of Revenue, DMV – International Registration Plan", "https://dmv.colorado.gov/international-registration-plan",
         "Port of Entry weigh stations and oversize/overweight permits are run by the Colorado State Patrol; household goods/passenger authority is regulated by the Colorado PUC."),
  "CT": ("Connecticut Department of Motor Vehicles – IRP/Commercial Vehicle Services", "https://portal.ct.gov/dmv/commercial-and-industry-services/apply-irp", None),
  "DE": ("Delaware Division of Motor Vehicles – Motor Carrier Services", "https://dmv.de.gov/services/MotorCarrier/index.shtml", None),
  "FL": ("Florida Department of Highway Safety and Motor Vehicles – International Registration Plan / Motor Carrier Services", "https://www.flhsmv.gov/driver-licenses-id-cards/commercial-motor-vehicle-drivers/international-registration-plan/",
         "Oversize/overweight permits are issued by FDOT's Motor Carrier Size & Weight office; roadside safety enforcement is handled by the Florida Highway Patrol's Office of Commercial Vehicle Enforcement."),
  "GA": ("Georgia Department of Revenue, Motor Vehicle Division – Georgia Trucking Portal (IRP)", "https://dor.georgia.gov/motor-vehicles/georgia-trucking-portal",
         "Safety compliance and certificates for intrastate household-goods/passenger carriers are handled by the Georgia Dept. of Public Safety, Commercial Vehicle Enforcement Division."),
  "HI": ("Hawaii Public Utilities Commission – Motor Carrier Branch", "https://puc.hawaii.gov/motor_carriers/",
         "Hawaii does not participate in IRP or IFTA."),
  "ID": ("Idaho Transportation Department – Motor Carrier Services", "https://trucking.idaho.gov/", None),
  "IL": ("Illinois Commerce Commission – Transportation Division", "https://icc.illinois.gov/transportation/",
         "The ICC grants intrastate operating authority; IRP/IFTA vehicle registration is handled separately by the Illinois Secretary of State (Commercial & Farm Trucks)."),
  "IN": ("Indiana Department of Revenue – Motor Carrier Services", "https://www.in.gov/dor/motor-carrier-services/", None),
  "IA": ("Iowa Department of Transportation – Motor Carrier Services", "https://iowadot.gov/motor-carriers", None),
  "KS": ("Kansas Department of Revenue, Division of Vehicles – Trucking Through Kansas", "https://www.ksrevenue.gov/dovtruckingks.html", None),
  "KY": ("Kentucky Transportation Cabinet – Division of Motor Carriers", "https://drive.ky.gov/Motor-Carriers/Pages/default.aspx", None),
  "LA": ("Louisiana Office of Motor Vehicles – International Registration Plan", "https://expresslane.la.gov/omv/vehicles/international-registration-plan/",
         "IFTA fuel tax licensing is administered separately by the Louisiana Department of Revenue."),
  "ME": ("Maine Bureau of Motor Vehicles – Motor Carrier Services", "https://www.maine.gov/sos/bmv/vehicles/commercial-vehicles-motor-carrier-services", None),
  "MD": ("Maryland MDOT Motor Vehicle Administration – International Registration Program", "https://mva.maryland.gov/vehicles/Pages/registration/irp.aspx",
         "Oversize/overweight hauling permits are issued by MDOT State Highway Administration."),
  "MA": ("Massachusetts Registry of Motor Vehicles – International Registration Plan (IRP)", "https://www.mass.gov/how-to/apply-for-an-international-registration-plan-irp-registration",
         "IFTA fuel tax is administered separately by the Massachusetts Dept. of Revenue via MassTaxConnect."),
  "MI": ("Michigan Department of State – International Registration Plan (IRP)", "https://www.michigan.gov/sos/industry-services/irp",
         "IFTA fuel tax is administered separately by the Michigan Department of Treasury."),
  "MN": ("Minnesota Department of Public Safety – Driver and Vehicle Services (IRP and IFTA)", "https://dps.mn.gov/divisions/dvs/business/irp-and-ifta", None),
  "MS": ("Mississippi Department of Revenue – Interstate Commercial Vehicles (IRP)", "https://www.dor.ms.gov/business/interstate-commercial-vehicles",
         "Oversize/overweight permits are issued by MDOT's Permit & Motor Carrier Division."),
  "MO": ("Missouri Department of Transportation – Motor Carrier Services", "https://www.modot.org/mcs", None),
  "MT": ("Montana Department of Transportation – Motor Carrier Services Division", "https://www.mdt.mt.gov/business/mcs/", None),
  "NE": ("Nebraska Department of Motor Vehicles – Motor Carrier/Trucking", "https://dmv.nebraska.gov/mc/index", None),
  "NV": ("Nevada Department of Motor Vehicles – Motor Carrier Division", "https://dmv.nv.gov/mcoverview.htm", None),
  "NH": ("New Hampshire Division of Motor Vehicles – Motor Carriers", "https://www.dmv.nh.gov/motor-carriers",
         "IFTA is administered separately by the NH Department of Revenue Administration."),
  "NJ": ("New Jersey Motor Vehicle Commission – IRP/IFTA Permit Process", "https://www.nj.gov/mvc/business/irpiftaprocess.htm", None),
  "NM": ("New Mexico Motor Vehicle Division – Commercial Vehicles", "https://www.mvd.newmexico.gov/commercial/resources-and-information/", None),
  "NY": ("New York State Department of Motor Vehicles – Motor Carriers", "https://dmv.ny.gov/business/motor-carriers",
         "Highway Use Tax (HUT) and oversize/overweight permits are also processed via NYSDOT's OSCAR one-stop system."),
  "NC": ("North Carolina DMV – Commercial Trucking (IRP)", "https://www.ncdot.gov/dmv/title-registration/commercial-trucking/Pages/default.aspx",
         "IFTA is administered separately by the NC Department of Revenue."),
  "ND": ("North Dakota Department of Transportation – Motor Carrier Services", "https://www.dot.nd.gov/motor-vehicle/motor-carrier-services", None),
  "OH": ("Ohio Bureau of Motor Vehicles (Dept. of Public Safety) – International Registration Plan", "https://www.bmv.ohio.gov/vr-irp-geninfo.aspx",
         "IFTA is administered separately by the Ohio Department of Taxation."),
  "OK": ("Oklahoma Corporation Commission – Transportation Division (Trucking)", "https://oklahoma.gov/occ/divisions/transportation/trucking.html", None),
  "OR": ("Oregon Department of Transportation – Commerce and Compliance Division", "https://www.oregon.gov/odot/mct/pages/index.aspx",
         "Day-to-day permitting/filing is done through the state's official portal, oregontruckingonline.com."),
  "PA": ("Pennsylvania Public Utility Commission – Motor Carrier Services", "https://www.puc.pa.gov/motor-carrier/",
         "The PUC issues certificates for household-goods/passenger for-hire carriers. Apportioned (IRP) registration is handled by PennDOT's Bureau of Motor Vehicles; IFTA by the PA Department of Revenue."),
  "RI": ("Rhode Island Division of Motor Vehicles – International Registration Plan (IRP)", "https://dmv.ri.gov/registrations-plates-titles/international-registration-plan-irp",
         "IFTA is administered separately by the RI Division of Taxation."),
  "SC": ("South Carolina Department of Motor Vehicles – Motor Carriers", "https://dmv.sc.gov/business-customers/motor-carriers", None),
  "SD": ("South Dakota Department of Revenue – Motor Carrier Services", "https://dor.sd.gov/businesses/motor-vehicle/motor-carrier-services/", None),
  "TN": ("Tennessee Department of Revenue – Motor Carrier", "https://www.tn.gov/revenue/motor-carrier.html", None),
  "TX": ("Texas Department of Motor Vehicles – Motor Carrier Division", "https://www.txdmv.gov/motor-carriers", None),
  "UT": ("Utah Department of Transportation – Motor Carrier Operating Authority", "https://www.udot.utah.gov/connect/business/motor-carriers/motor-carrier-registration-credentials/motor-carrier-operating-authority/",
         "IRP/IFTA registration and fuel tax are administered separately by the Utah State Tax Commission, Motor Carrier Services."),
  "VT": ("Vermont Department of Motor Vehicles – Commercial Vehicle Operations", "https://dmv.vermont.gov/CVO", None),
  "VA": ("Virginia Department of Motor Vehicles – Motor Carrier Services", "https://www.dmv.virginia.gov/businesses/motor-carriers", None),
  "WA": ("Washington State Department of Licensing – Prorate and Fuel Tax (Motor Carrier Services)", "https://dol.wa.gov/vehicles-and-boats/prorate-and-fuel-tax", None),
  "WV": ("West Virginia Division of Motor Vehicles – IRP & IFTA (Motor Carriers)", "https://transportation.wv.gov/DMV/Motor-Carriers/Pages/IRP-IFTA.aspx", None),
  "WI": ("Wisconsin Department of Transportation, Division of Motor Vehicles – Motor Carriers and Trucking", "https://wisconsindot.gov/Pages/dmv/com-drv-vehs/mtr-car-trkr/default.aspx", None),
  "WY": ("Wyoming Department of Transportation – Motor Vehicle Services", "https://www.dot.state.wy.us/home/trucking_commercial_vehicles.html",
         "We could not fully confirm this link is still current — if it doesn't load, search \"Wyoming DOT motor carrier services\" for the current page."),
}

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
