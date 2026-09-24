# Guide pages and free tools. Run through tools/build_site.py, which defines head(), header(), FOOTER, write() and SITE.
# Every guide is general information with sources, never advice, and ends by pointing to the directory.
# A guide stays marked "waiting for consultant review" until a listed consultant has reviewed it (set reviewed_by).

GUIDES_UPDATED = "September 24, 2026"
GUIDES_ISO = "2026-09-24"

def src(label, url):
    return (label, url)

FMCSA_FAQ = src("FMCSA: What would cause a carrier to fail a new entrant safety audit?", "https://www.fmcsa.dot.gov/faq/what-would-cause-motor-carrier-fail-new-entrant-safety-audit-ss-385321")
ECFR_NE = src("eCFR: 49 CFR Part 385, Subpart D (New Entrant Safety Assurance Program)", "https://www.ecfr.gov/current/title-49/subtitle-B/chapter-III/subchapter-B/part-385/subpart-D")
ECFR_321 = src("eCFR: 49 CFR 385.321, Safety audit failure", "https://www.ecfr.gov/current/title-49/subtitle-B/chapter-III/subchapter-B/part-385/subpart-D/section-385.321")
CAP_PDF = src("FMCSA: Corrective Action Plan guidance for failed safety audits (PDF)", "https://ai.fmcsa.dot.gov/NewEntrant/Data/Docs/CAP_Guidance.pdf")
NE_HELP = src("FMCSA New Entrant help center", "https://ai.fmcsa.dot.gov/NewEntrant/HelpCenter.aspx")
ECFR_382 = src("eCFR: 49 CFR Part 382, Drug and alcohol testing", "https://www.ecfr.gov/current/title-49/subtitle-B/chapter-III/subchapter-B/part-382")
CH_OO = src("FMCSA Clearinghouse: Owner-operator brochure (PDF)", "https://clearinghouse.fmcsa.dot.gov/content/resources/Clearinghouse-Brochure-Owner-Operator.pdf")
CH_PLANS = src("FMCSA Clearinghouse: Query plans", "https://clearinghouse.fmcsa.dot.gov/query/plan")
CSA_JJK = src("J. J. Keller: FMCSA interventions for BASIC scores above the threshold", "https://www.jjkeller.com/learn/csa-interventions")
OOIDA_WL = src("OOIDA: Warning letter tip sheet (PDF)", "https://www.ooida.com/wp-content/uploads/2016/04/WarningLetterTipsheet1.pdf")
DATAQS = src("FMCSA DataQs", "https://dataqs.fmcsa.dot.gov/")
SMS = src("FMCSA Safety Measurement System (SMS)", "https://ai.fmcsa.dot.gov/SMS/")
ECFR_390_19 = src("eCFR: 49 CFR 390.19, Registration and biennial updates", "https://www.ecfr.gov/current/title-49/subtitle-B/chapter-III/subchapter-B/part-390/subpart-A/section-390.19")
CVSA_RC = src("CVSA: International Roadcheck 2026", "https://cvsa.org/news/2026-roadcheck/")
CVSA_BSW = src("CVSA: Brake Safety Week 2026", "https://cvsa.org/news/2026-bsw-dates/")
UCR = src("Unified Carrier Registration plan", "https://plan.ucr.gov/")
IRS_2290 = src("IRS: About Form 2290", "https://www.irs.gov/forms-pubs/about-form-2290")
IFTA = src("IFTA, Inc.", "https://www.iftach.org/")

CTA_LAUNCH = '''<aside class="guide-cta">
  <h2>Want someone to handle this?</h2>
  <p>An independent DOT compliance consultant can check your records and do this work for you. Our consultant directory opens in 2027. Until then, look for someone with safety audit experience and ask for references.</p>
</aside>'''
CTA = '''<aside class="guide-cta">
  <h2>Want someone to handle this?</h2>
  <p>Independent DOT compliance consultants on FleetCleared do this work for small carriers every day. Free to search, and nobody contacts you unless you ask.</p>
  <a class="btn btn-primary" href="browse.html">Find a consultant</a>
</aside>'''

DISCLAIMER = '<p class="fine guide-disclaimer">General information, not legal or compliance advice, and no substitute for the regulations or a qualified professional. Rules change and every carrier is different. Reading this page doesn\'t create a relationship with FleetCleared or any consultant, and using it is subject to our <a href="terms.html#guides">terms</a>. Found an error? Email <strong>corrections@fleetcleared.com</strong>. FleetCleared is a directory and is not affiliated with FMCSA or the U.S. Department of Transportation.</p>'

GUIDES = []   # (slug, card title, card blurb, group)
GUIDE_PAGES = ["guides.html"]

def guide_scripts(extra):
    return FOOTER.replace('</body>', extra.lstrip('\n') + '\n</body>', 1)

def guide(slug, title, desc, h1, answer, sections, sources, related, group, card, blurb, tool_html="", scripts=""):
    """sections: list of (id, heading, html)."""
    GUIDES.append((slug, card, blurb, group))
    GUIDE_PAGES.append(slug)
    LAUNCH_PAGES.add(slug)
    toc = "".join(f'<li><a href="#{i}">{h}</a></li>' for i, h, _ in sections)
    body = "".join(f'<h2 id="{i}">{h}</h2>\n{c}\n' for i, h, c in sections)
    srcs = "".join(f'<li><a href="{u}" rel="noopener">{l}</a></li>' for l, u in sources)
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Article", "headline": h1, "description": desc, "dateModified": GUIDES_ISO, "datePublished": GUIDES_ISO,
             "mainEntityOfPage": f"{SITE}/{slug}", "publisher": {"@id": f"{SITE}/#org"}, "author": {"@type": "Organization", "@id": f"{SITE}/#org", "name": "FleetCleared"}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Guides", "item": f"{SITE}/guides.html"},
                {"@type": "ListItem", "position": 2, "name": card, "item": f"{SITE}/{slug}"}]},
        ],
    }
    extra = f'\n<script type="application/ld+json">{json.dumps(ld)}</script>'
    rel = "".join(f'<a class="tour-card" href="{s}"><span class="variation">{g}</span><b>{c}</b><span>{b}</span></a>'
                  for s, c, b, g in RELATED_INDEX if s in related)
    nav_key = "mcs" if slug == "mcs-150-due-date.html" else "check" if slug == "audit-readiness-check.html" else "guides"
    write(slug, head(title, desc, slug, extra) + header(nav_key) + f'''<main class="wrap">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="guides.html">Guides</a> <span aria-hidden="true">/</span> <span>{card}</span></nav>
  <div class="page-head guide-head">
    <h1>{h1}</h1>
    <div class="short-answer"><span class="eyebrow">Short answer</span><p>{answer}</p></div>
    <p class="guide-meta">Updated {GUIDES_UPDATED}{"" if LAUNCH else ' · <span class="review-pending">Waiting for review by a listed consultant</span>'}</p>
    <p class="guide-notice">General information, not legal advice. Rules change: check the linked sources or a qualified consultant before acting. <a href="terms.html#guides">How to use our guides</a></p>
  </div>
  {tool_html}
  <div class="legal guide">
    <aside class="legal-toc"><p>On this page</p><ol>{toc}<li><a href="#sources">Sources</a></li></ol></aside>
    <article class="legal-body">
{body}
      {CTA_LAUNCH if LAUNCH else CTA}
      <h2 id="sources">Sources</h2>
      <ul class="sources">{srcs}</ul>
      {DISCLAIMER}
    </article>
  </div>
  <section class="related"><h2>Keep reading</h2><div class="tour-grid">{rel}</div></section>
</main>
''' + guide_scripts(scripts))

# Card index used for "Keep reading" and the hub. Filled before pages are written.
RELATED_INDEX = [
    ("guide-new-entrant-safety-audit.html", "How to pass the new entrant safety audit", "What the auditor checks, the records to have ready, and how most carriers pass.", "New carriers"),
    ("guide-automatic-fail-violations.html", "The 16 violations that fail you automatically", "Each one in plain words, most common first, and how to avoid it.", "New carriers"),
    ("guide-failed-safety-audit.html", "Failed your safety audit? Your deadlines", "15 days to send a plan, 45 or 60 days before revocation. What to send.", "New carriers"),
    ("audit-readiness-check.html", "Audit readiness check", "Ten yes-or-no questions. See which automatic-fail rules you might be breaking.", "Free tool"),
    ("guide-drug-alcohol-consortium.html", "Do I need a drug and alcohol consortium?", "Who's covered, what a program needs, and why owner-operators must join one.", "Drug and alcohol"),
    ("guide-clearinghouse-queries.html", "Clearinghouse queries: full vs. limited", "Which query you need before hiring and every year, and what it costs.", "Drug and alcohol"),
    ("guide-csa-warning-letter.html", "Got a CSA warning letter? What to do", "What it means, the score thresholds, and the steps that head off an investigation.", "Trouble"),
    ("mcs-150-due-date.html", "When is my MCS-150 due?", "Enter your USDOT number and see the month your update is due.", "Free tool"),
    ("guide-compliance-calendar.html", "The small carrier's compliance calendar", "Every yearly deadline and inspection week, month by month.", "Deadlines"),
]

# ---------------------------------------------------------------- guides
AUTOFAIL = [
    # plain name, regulation, what it means, how to avoid, how common, takes
    ("No random drug and alcohol testing program", "382.305", "Your CDL drivers, including you if you drive, aren't in a random testing pool.", "Join a consortium or set up your own random pool before your first CDL driver works.", "Most common", "One instance"),
    ("No drug and alcohol testing program at all", "382.115", "No testing program was in place when a CDL driver started working.", "Have a written policy and a negative pre-employment drug test before anyone drives.", "Most common", "One instance"),
    ("Trucks without a yearly inspection", "396.17(a)", "No annual inspection record for the vehicles checked.", "Inspect every truck and trailer at least once every 12 months and keep the report.", "Common", "51% or more of records checked"),
    ("Drivers not keeping hours-of-service logs", "395.8(a)", "Drivers aren't required to record their hours.", "Use an ELD or paper logs unless a written exemption applies, and keep the records.", "Common", "51% or more of records checked"),
    ("Driver without a valid medical card", "391.11(b)(4)", "A driver isn't medically qualified.", "Keep a current DOT medical certificate for every driver and track expiry dates.", "Common", "One instance"),
    ("Operating without the minimum insurance", "387.7(a)", "Liability coverage is below the federal minimum for what you haul.", "Confirm your limits with your agent. General freight is usually $750,000.", "Occasional", "One instance"),
    ("Driver-reported defect not fixed", "396.11(c)", "A driver wrote up an out-of-service defect and the truck ran again before repair.", "Repair it, sign the report, and keep it before the truck moves.", "Occasional", "One instance"),
    ("Driving a truck put out of service", "396.9(c)(2)", "A truck ordered out of service at an inspection moved before it was repaired.", "Repair first, then return the signed inspection report as instructed.", "Occasional", "One instance"),
    ("Driver without a valid CDL", "383.3(a) / 383.23(a)", "A driver needs a CDL for the vehicle and doesn't have one.", "Check the license class and endorsements against every vehicle they drive.", "Occasional", "One instance"),
    ("Using a disqualified driver", "391.15(a)", "A driver is disqualified under driver-qualification rules.", "Pull a driving record at hire and every year, and act on what it shows.", "Rare", "One instance"),
    ("Using a driver disqualified from holding a CDL", "383.51(a)", "A driver lost CDL privileges, for example after a DUI.", "Same as above: driving records at hire and yearly.", "Rare", "One instance"),
    ("Using a driver whose license is suspended or revoked", "383.37(b)", "You knew, or should have known, the license wasn't valid.", "Same as above, plus a written rule that drivers report suspensions.", "Rare", "One instance"),
    ("Using a driver who tested positive for drugs", "382.215", "A driver kept working after a positive test.", "Remove them from driving until they finish the return-to-duty process.", "Rare", "One instance"),
    ("Using a driver who refused a test", "382.211", "A refusal counts like a positive, and the driver kept working.", "Treat a refusal exactly like a positive result.", "Rare", "One instance"),
    ("Using a driver with alcohol at 0.04 or higher", "382.201", "A driver worked at or above 0.04 alcohol concentration.", "Remove them from driving and follow the return-to-duty process.", "Rare", "One instance"),
    ("Passenger vehicle without the minimum insurance", "387.31(a)", "A bus or passenger van ran below the required coverage.", "Passenger carriers only: confirm limits for your seating capacity.", "Rare (passenger only)", "One instance"),
]

guide("guide-new-entrant-safety-audit.html",
  "How to Pass the FMCSA New Entrant Safety Audit (2026) | FleetCleared",
  "Every new carrier gets an FMCSA safety audit in its first 12 months. What the auditor checks, the records to have ready, and the 16 violations that fail you automatically.",
  "How to pass the FMCSA new entrant safety audit",
  "Every new carrier gets a safety audit within its first 12 months of operating. You pass if the auditor finds none of the 16 automatic-fail violations and your records show basic safety controls: a drug and alcohol program, driver files, hours-of-service logs, maintenance records and insurance.",
  [
    ("what", "What the audit is", '''<p>When you get a USDOT number for interstate operations, you enter an 18-month new entrant monitoring period. During the first 12 months, FMCSA or a state partner audits your safety records. Passenger carriers are audited within the first 120 days.</p>
<p>The audit can happen at your place of business or off-site, where you upload records. Either way you get a notice first, with a list of what to have ready.</p>
<p>Most carriers pass. FMCSA ran 63,672 audits in 2022 with a 92.2% pass rate, and 58,600 in 2023 with a 91.3% pass rate. That still means thousands of carriers fail every year, usually over records they could have fixed in advance.</p>'''),
    ("checks", "What the auditor checks", '''<div class="table-wrap"><table>
<thead><tr><th>Area</th><th>Records to have ready</th></tr></thead><tbody>
<tr><td><b>Drug and alcohol</b></td><td>Written policy, consortium or random pool enrollment, pre-employment test results, random selection records, Clearinghouse queries. Only for carriers with CDL drivers.</td></tr>
<tr><td><b>Driver files</b></td><td>For every driver: application, license copy, medical certificate, driving record from each state, past employer safety checks, annual review.</td></tr>
<tr><td><b>Hours of service</b></td><td>ELD records or paper logs and supporting documents such as fuel receipts and bills of lading.</td></tr>
<tr><td><b>Vehicles</b></td><td>Annual inspection reports, repair and maintenance records, driver vehicle inspection reports for each truck and trailer.</td></tr>
<tr><td><b>Insurance and accidents</b></td><td>Proof of the required insurance, and an accident register, even if it's empty.</td></tr>
</tbody></table></div>'''),
    ("autofail", "The 16 violations that fail you automatically", '''<p>Most findings only count against you. These 16 end the audit on their own. The most common by far are missing drug and alcohol testing:</p>
<ul>
<li>No random drug and alcohol testing program</li>
<li>No drug and alcohol testing program at all</li>
<li>Trucks without a yearly inspection (on half or more of the records checked)</li>
<li>No hours-of-service logs (on half or more of the records checked)</li>
<li>A driver without a valid medical card</li>
</ul>
<p><a href="guide-automatic-fail-violations.html">See all 16 in plain words</a>, or take the <a href="audit-readiness-check.html">audit readiness check</a>.</p>'''),
    ("before", "Checklist for the weeks before", '''<ul>
<li>Open a folder for every driver and check each item in the driver-file row above.</li>
<li>Confirm every CDL driver, including you, is in a random testing pool, and keep the enrollment certificate.</li>
<li>Run a Clearinghouse query on every CDL driver if you haven't in the last 12 months.</li>
<li>Pull 30 days of logs for each driver and check for missing days and violations.</li>
<li>Make sure every truck and trailer has an annual inspection report dated within the last 12 months.</li>
<li>Print your insurance proof and start an accident register if you don't have one.</li>
<li>Answer the audit notice by its deadline. Ignoring it can be treated as a failure.</li>
</ul>'''),
    ("fail", "If you fail", '''<p>You get a written notice. Send a corrective action plan within 15 days so FMCSA has time to review it. Property carriers have 60 days from the notice to show acceptable corrective action; passenger and placarded hazmat carriers have 45. Miss it and your registration is revoked. <a href="guide-failed-safety-audit.html">Read what to do after a failed audit</a>.</p>'''),
    ("help", "When to get help", '''<p>No checklist guarantees a pass: auditors review your actual records and can find problems beyond the 16 automatic-fail rules. Many carriers prepare on their own. A consultant is worth it if you have several drivers, you're behind on driver files, you've never set up drug and alcohol testing, or your audit is weeks away. Many offer a mock audit that walks through your records the way the auditor will.</p>'''),
  ],
  [FMCSA_FAQ, ECFR_NE, ECFR_321, NE_HELP],
  ["guide-automatic-fail-violations.html", "guide-failed-safety-audit.html", "audit-readiness-check.html", "guide-drug-alcohol-consortium.html"],
  "New carriers", "How to pass the new entrant safety audit", "")

af_rows = "".join(f'<tr><td class="num">{i}</td><td><b>{n}</b><br><span class="hint">49 CFR {r} · {t}</span></td><td>{m}</td><td>{a}</td><td>{c}</td></tr>' for i, (n, r, m, a, c, t) in enumerate(AUTOFAIL, 1))
guide("guide-automatic-fail-violations.html",
  "The 16 Automatic-Fail Violations in the New Entrant Safety Audit | FleetCleared",
  "The 16 regulations that fail an FMCSA new entrant safety audit on their own, explained in plain words, most common first, with how to avoid each one.",
  "The 16 violations that fail your safety audit automatically",
  "FMCSA lists 16 regulations that fail a new entrant safety audit on their own. Fourteen fail you on a single instance; missing yearly truck inspections and missing hours-of-service logs fail you when they show up in half or more of the records checked.",
  [
    ("list", "All 16, most common first", f'''<p>FMCSA doesn't publish counts for each rule. The order below comes from consultant and industry reports, which consistently put drug and alcohol testing at the top.</p>
<div class="table-wrap"><table><thead><tr><th>#</th><th>What fails you</th><th>What it means</th><th>How to avoid it</th><th>How common</th></tr></thead><tbody>{af_rows}</tbody></table></div>'''),
    ("cdl", "If your drivers don't need a CDL", '''<p>Seven of the 16 only apply to carriers with CDL drivers: the five drug and alcohol rules and the CDL rules. If you run box trucks under 26,001 pounds without placarded hazmat and without CDL drivers, the drug and alcohol testing rules in Part 382 don't cover you. Driver files, medical cards, logs, inspections and insurance still do.</p>'''),
    ("check", "Check yourself in two minutes", '''<p>The <a href="audit-readiness-check.html">audit readiness check</a> turns these 16 rules into ten yes-or-no questions and shows which ones to fix first. Nothing you enter is saved or sent.</p>'''),
  ],
  [ECFR_321, FMCSA_FAQ, ECFR_NE],
  ["guide-new-entrant-safety-audit.html", "audit-readiness-check.html", "guide-failed-safety-audit.html", "guide-drug-alcohol-consortium.html"],
  "New carriers", "The 16 violations that fail you automatically", "")

guide("guide-failed-safety-audit.html",
  "Failed Your New Entrant Safety Audit? Deadlines and What to Do | FleetCleared",
  "After a failed FMCSA safety audit you have 15 days to send a corrective action plan, and 45 or 60 days before your registration is revoked. What to send and what to avoid.",
  "Failed your safety audit? Your deadlines and what to do next",
  "Send FMCSA a corrective action plan within 15 days of the failure notice. Property carriers have 60 days from the notice to show acceptable corrective action, and passenger and placarded hazmat carriers have 45. If you miss it, your registration is revoked and you're placed out of service.",
  [
    ("timeline", "Your timeline", '''<div class="table-wrap"><table><thead><tr><th>When</th><th>What happens</th></tr></thead><tbody>
<tr><td class="num">Day 0</td><td>You receive the written notice that you failed.</td></tr>
<tr><td class="num">By day 15</td><td>Submit your corrective action plan, so FMCSA has time to review it before the deadline.</td></tr>
<tr><td class="num">Day 45</td><td>Deadline for passenger carriers and placarded hazmat carriers.</td></tr>
<tr><td class="num">Day 60</td><td>Deadline for property carriers.</td></tr>
<tr><td class="num">Day 46 or 61</td><td>Without accepted corrective action: registration revoked and an out-of-service order takes effect.</td></tr>
</tbody></table></div>
<p>Count from the date on your notice, not the day you open it.</p>'''),
    ("cap", "What a corrective action plan needs", '''<p>For each violation listed on your notice:</p>
<ul>
<li><b>What went wrong,</b> in one or two plain sentences.</li>
<li><b>What you changed,</b> with the date.</li>
<li><b>Proof,</b> such as a consortium enrollment certificate, a completed driver file, an annual inspection report, or ELD setup confirmation.</li>
<li><b>How you'll keep it from happening again:</b> who is responsible and how often they check.</li>
</ul>
<p>FMCSA publishes guidance on what an acceptable plan contains. Read it before you write yours.</p>'''),
    ("mistakes", "Mistakes that get plans rejected", '''<ul>
<li>Promises without proof ("we will enroll drivers").</li>
<li>Fixing some violations and skipping others.</li>
<li>Sending it close to the deadline, with no time to correct a rejected plan.</li>
<li>Keeping the problem going while the plan is under review, such as letting an unenrolled driver keep driving.</li>
</ul>'''),
    ("review", "If you think the audit got it wrong", '''<p>You can ask FMCSA for an administrative review of a failed audit. Your notice explains how and by when. You can do this and still send a corrective action plan; don't let one wait on the other.</p>'''),
    ("help", "When to get help", '''<p>This is the moment most carriers call a consultant. Someone who writes these plans regularly knows what reviewers accept, and the clock doesn't stop while you learn.</p>'''),
  ],
  [CAP_PDF, ECFR_NE, NE_HELP],
  ["guide-new-entrant-safety-audit.html", "guide-automatic-fail-violations.html", "guide-drug-alcohol-consortium.html", "audit-readiness-check.html"],
  "New carriers", "Failed your safety audit? Your deadlines", "")

guide("guide-drug-alcohol-consortium.html",
  "Do I Need a Drug and Alcohol Consortium? Owner-Operators and Small Fleets | FleetCleared",
  "If you or your drivers need a CDL, you need a DOT drug and alcohol testing program with random testing. Why owner-operators must join a consortium, and what the program includes.",
  "Do I need a drug and alcohol consortium?",
  "If anyone at your company drives a vehicle that requires a CDL, you need a DOT drug and alcohol testing program with random testing. An owner-operator must join a consortium, because one person can't be their own random pool. Carriers whose drivers don't need a CDL aren't covered by these testing rules.",
  [
    ("who", "Who's covered", '''<p>The testing rules in 49 CFR Part 382 cover drivers of vehicles that require a CDL: generally 26,001 pounds or more, 16 or more passengers including the driver, or hazardous materials that require placards.</p>
<p>No random testing program is the single most common reason new carriers fail their safety audit, and it fails you on the first instance.</p>'''),
    ("program", "What the program needs", '''<ul>
<li>A written drug and alcohol policy given to every driver.</li>
<li>A negative pre-employment drug test before a driver's first run.</li>
<li>Random testing. For 2026 the minimum yearly rates are 50% of drivers for drugs and 10% for alcohol.</li>
<li>Post-accident and reasonable-suspicion testing, with a supervisor trained to spot signs of use.</li>
<li>Return-to-duty and follow-up testing after a violation.</li>
<li>Clearinghouse registration and queries. <a href="guide-clearinghouse-queries.html">See which queries you need</a>.</li>
<li>A named person who receives results and removes drivers from duty (the designated employer representative).</li>
</ul>'''),
    ("consortium", "What a consortium does", '''<p>A consortium, or third-party administrator (C/TPA), puts your drivers into a larger random pool, handles selections, schedules tests and keeps the records. Owner-operators must use one and must name it in the Clearinghouse. Larger fleets can run their own pool, but most small carriers use a consortium.</p>
<p>Prices vary. Ask what's included: random selections, collection sites near you, Clearinghouse reporting, supervisor training and audit-ready records.</p>'''),
    ("notcdl", "If your drivers don't need a CDL", '''<p>Part 382 doesn't apply. You still need driver files, medical cards where required, hours-of-service records and vehicle maintenance. Some customers and insurers require testing anyway.</p>'''),
  ],
  [ECFR_382, CH_OO, ECFR_321],
  ["guide-clearinghouse-queries.html", "guide-automatic-fail-violations.html", "guide-new-entrant-safety-audit.html", "audit-readiness-check.html"],
  "Drug and alcohol", "Do I need a drug and alcohol consortium?", "")

guide("guide-clearinghouse-queries.html",
  "FMCSA Clearinghouse Queries: Full vs. Limited, Explained | FleetCleared",
  "Run a full Clearinghouse query before hiring a CDL driver and a limited query on every CDL driver at least once a year. What each one needs and what to do if a limited query shows a record.",
  "Clearinghouse queries: full vs. limited",
  "Run a full query before a CDL driver's first run, with the driver's consent given inside the Clearinghouse. Run at least a limited query on every CDL driver once every 12 months. If a limited query shows a record exists, you have 24 hours to run a full query or the driver can't keep driving.",
  [
    ("types", "The two kinds of query", '''<div class="table-wrap"><table><thead><tr><th></th><th>Full query</th><th>Limited query</th></tr></thead><tbody>
<tr><td><b>When</b></td><td>Before hiring, and within 24 hours after a limited query shows a record</td><td>At least once every 12 months for every CDL driver</td></tr>
<tr><td><b>Shows</b></td><td>Details of any violation and its return-to-duty status</td><td>Only whether a record exists</td></tr>
<tr><td><b>Driver consent</b></td><td>Given electronically in the Clearinghouse, so the driver must be registered</td><td>A written consent you keep on file; one can cover several years</td></tr>
</tbody></table></div>'''),
    ("cost", "What it costs", '''<p>Queries are bought in plans from FMCSA's Clearinghouse site. See the current price on the <a href="https://clearinghouse.fmcsa.dot.gov/query/plan" rel="noopener">query plans page</a>.</p>'''),
    ("oo", "Owner-operators", '''<p>If you're a one-truck operation, you're both the employer and the driver. You must name a consortium (C/TPA) in the Clearinghouse, and it handles queries and reporting for you. You remain responsible if it doesn't happen.</p>'''),
    ("audit", "Why it matters at your audit", '''<p>Missing pre-employment and annual queries show up in drug and alcohol findings at a safety audit. They sit right next to the most common automatic failure: no random testing program.</p>'''),
  ],
  [CH_PLANS, CH_OO, ECFR_382],
  ["guide-drug-alcohol-consortium.html", "guide-new-entrant-safety-audit.html", "guide-compliance-calendar.html"],
  "Drug and alcohol", "Clearinghouse queries: full vs. limited", "")

guide("guide-csa-warning-letter.html",
  "Got a CSA Warning Letter from FMCSA? What It Means and What to Do | FleetCleared",
  "A CSA warning letter means one of your BASIC scores is over FMCSA's threshold. The thresholds, the steps to take, and how to avoid an investigation.",
  "Got a CSA warning letter? What it means and what to do",
  "A warning letter means one of your seven CSA safety scores (BASICs) is above FMCSA's intervention threshold. You don't have to reply in writing, but fix the cause and challenge any wrong inspection records through DataQs. If the score stays high, FMCSA can open an off-site or on-site investigation.",
  [
    ("thresholds", "The thresholds", '''<p>Each BASIC is a percentile against similar carriers. The letter goes out when a score crosses these lines:</p>
<div class="table-wrap"><table><thead><tr><th>BASIC</th><th class="num">Most carriers</th><th class="num">Hazmat</th><th class="num">Passenger</th></tr></thead><tbody>
<tr><td>Unsafe Driving, Hours of Service, Crash Indicator</td><td class="num">65%</td><td class="num">60%</td><td class="num">50%</td></tr>
<tr><td>Vehicle Maintenance, Controlled Substances and Alcohol, Driver Fitness</td><td class="num">80%</td><td class="num">75%</td><td class="num">65%</td></tr>
<tr><td>Hazardous Materials Compliance (hazmat carriers only)</td><td class="num">—</td><td class="num">80%</td><td class="num">—</td></tr>
</tbody></table></div>'''),
    ("steps", "What to do, in order", '''<ol>
<li><b>Read which BASIC is flagged</b> and the time period the letter covers.</li>
<li><b>Pull your inspection list</b> from FMCSA's Safety Measurement System and find the violations driving the score.</li>
<li><b>Check each record for accuracy.</b> Wrong carrier, wrong vehicle, violations that were dismissed in court: challenge them through DataQs.</li>
<li><b>Fix the cause,</b> not just the paperwork: driver training, maintenance schedule, log audits.</li>
<li><b>Write down what you changed and when.</b> If an investigator comes later, this is your evidence.</li>
<li><b>Watch the monthly updates.</b> Scores recalculate as new inspections come in and old ones age out.</li>
</ol>'''),
    ("next", "If scores stay high", '''<p>FMCSA can assign an off-site investigation, where you send records, or an on-site one at your place of business. Either can end in a safety rating, and a Conditional or Unsatisfactory rating affects insurance and broker relationships.</p>'''),
    ("help", "When to get help", '''<p>Consultants handle DataQs challenges and root-cause fixes regularly. Getting help now, before an investigation, costs less than after one.</p>'''),
  ],
  [CSA_JJK, OOIDA_WL, SMS, DATAQS],
  ["guide-compliance-calendar.html", "guide-new-entrant-safety-audit.html", "guide-clearinghouse-queries.html"],
  "Trouble", "Got a CSA warning letter? What to do", "")

CAL = [
    ("January", ["IFTA fourth-quarter return due Jan 31", "UCR enforcement begins for carriers that haven't paid", "Many carriers run yearly driving-record reviews and Clearinghouse queries"]),
    ("February", ["Catch up on anything January missed"]),
    ("March", ["CVSA usually announces International Roadcheck dates and focus areas"]),
    ("April", ["IFTA first-quarter return due Apr 30", "Check trucks and files before Roadcheck"]),
    ("May", ["International Roadcheck: 72 hours of inspections across North America (2026: May 12–14)"]),
    ("June", ["Heavy vehicle use tax year ends Jun 30", "Challenge wrong Roadcheck inspection records through DataQs"]),
    ("July", ["IFTA second-quarter return due Jul 31", "Operation Safe Driver Week (driver behavior)", "New heavy vehicle use tax year starts Jul 1"]),
    ("August", ["Form 2290 (heavy vehicle use tax) due Aug 31", "Brake Safety Week (2026: Aug 23–29)"]),
    ("September", ["A quiet month: good time for a mock audit"]),
    ("October", ["UCR registration opens Oct 1 for next year", "IFTA third-quarter return due Oct 31"]),
    ("November", ["UCR registration continues"]),
    ("December", ["UCR due Dec 31", "Schedule next year's annual reviews and inspections"]),
]
cal_html = '<div class="cal-grid">' + "".join(f'<div class="cal-month"><h3>{m}</h3><ul>{"".join(f"<li>{e}</li>" for e in ev)}</ul></div>' for m, ev in CAL) + '</div>'
guide("guide-compliance-calendar.html",
  "Trucking Compliance Calendar: Every Yearly Deadline, Month by Month | FleetCleared",
  "IFTA, UCR, Form 2290, MCS-150 and the national inspection weeks, month by month, for small trucking companies.",
  "The small carrier's compliance calendar",
  "The fixed yearly dates are IFTA returns (Jan 31, Apr 30, Jul 31, Oct 31), Form 2290 (Aug 31) and UCR (Oct 1 to Dec 31). Your MCS-150 update month depends on your USDOT number, and national inspection weeks fall in May and August.",
  [
    ("months", "Month by month", cal_html),
    ("yours", "Dates that depend on you", '''<ul>
<li><b>MCS-150 update:</b> every two years, in a month set by your USDOT number. <a href="mcs-150-due-date.html">Find your month</a>.</li>
<li><b>Annual vehicle inspections:</b> within 12 months of each truck's last one.</li>
<li><b>Driver medical cards:</b> up to two years, often less. Track each expiry date.</li>
<li><b>Annual driving-record review and Clearinghouse query:</b> within 12 months for every driver.</li>
</ul>'''),
    ("note", "Check the dates each year", '''<p>Inspection weeks are announced by CVSA each year, and filing systems change. FMCSA moved registration to a new system, Motus, in 2026. Confirm dates with the official sources below.</p>'''),
  ],
  [UCR, IRS_2290, IFTA, CVSA_RC, CVSA_BSW, ECFR_390_19],
  ["mcs-150-due-date.html", "guide-clearinghouse-queries.html", "guide-new-entrant-safety-audit.html"],
  "Deadlines", "The small carrier's compliance calendar", "")

# ---------------------------------------------------------------- tools
MCS_TOOL = '''<section class="tool-card" aria-labelledby="mcs-tool-h">
  <h2 id="mcs-tool-h">Find your MCS-150 month</h2>
  <form id="mcs-form" class="tool-form" novalidate>
    <div class="field"><label for="mcs-usdot">USDOT number</label><input id="mcs-usdot" inputmode="numeric" autocomplete="off" placeholder="e.g. 3456789" required></div>
    <button class="btn btn-primary" type="submit">Show my due date</button>
  </form>
  <p class="field-error" id="mcs-error" hidden></p>
  <div class="tool-result" id="mcs-result" hidden aria-live="polite"></div>
  <p class="fine">An estimate worked out on your device from the schedule in 49 CFR 390.19. Confirm your due date in your FMCSA registration before relying on it. Nothing is saved or sent.</p>
</section>'''
guide("mcs-150-due-date.html",
  "When Is My MCS-150 Due? Free USDOT Number Lookup | FleetCleared",
  "Enter your USDOT number to see the month and year your MCS-150 biennial update is due. Free, instant, nothing saved.",
  "When is my MCS-150 due?",
  "Every carrier updates its MCS-150 every two years. The last digit of your USDOT number sets the month (1 is January, 9 is September, 0 is October) and the next-to-last digit sets the year: odd digit in odd years, even digit in even years.",
  [
    ("how", "How the schedule works", '''<div class="table-wrap"><table><thead><tr><th>Last digit</th><th>Month</th><th>Last digit</th><th>Month</th></tr></thead><tbody>
<tr><td class="num">1</td><td>January</td><td class="num">6</td><td>June</td></tr>
<tr><td class="num">2</td><td>February</td><td class="num">7</td><td>July</td></tr>
<tr><td class="num">3</td><td>March</td><td class="num">8</td><td>August</td></tr>
<tr><td class="num">4</td><td>April</td><td class="num">9</td><td>September</td></tr>
<tr><td class="num">5</td><td>May</td><td class="num">0</td><td>October</td></tr>
</tbody></table></div>
<p>Example: USDOT 3456789 ends in 8 and 9. The last digit 9 means September. The next-to-last digit 8 is even, so the update is due in September of even-numbered years.</p>'''),
    ("miss", "If you miss it", '''<p>FMCSA can deactivate your USDOT number and assess civil penalties of up to $1,000 a day, capped at $10,000, adjusted for inflation. An inactive number can cut off your insurance filings and your access to loads.</p>
<p>FMCSA moved registration to a new system, Motus, in 2026 and paused some enforcement during the switch. Check FMCSA's site for the current status before you count on it.</p>'''),
    ("free", "Filing is free", '''<p>You can file the update directly with FMCSA at no cost. Companies that charge to "file your MCS-150" are optional services, and some send official-looking letters. FMCSA doesn't charge for this update.</p>'''),
  ],
  [ECFR_390_19],
  ["guide-compliance-calendar.html", "guide-new-entrant-safety-audit.html", "audit-readiness-check.html"],
  "Free tool", "When is my MCS-150 due?", "",
  tool_html=MCS_TOOL, scripts='\n<script src="assets/deadlines.js"></script>\n<script src="assets/guides.js" defer></script>')

QUESTIONS = [
    # id, cdl_only, question, rule label
    ("random", True, "Are all your CDL drivers, including you if you drive, in a random drug and alcohol testing pool?", "No random testing program"),
    ("program", True, "Do you have a written drug and alcohol policy, and did every CDL driver pass a pre-employment drug test before driving?", "No drug and alcohol program"),
    ("inspection", False, "Does every truck and trailer have an annual inspection report dated within the last 12 months?", "Trucks without a yearly inspection"),
    ("logs", False, "Does every driver keep hours-of-service logs (ELD or paper), unless a written exemption applies?", "No hours-of-service logs"),
    ("medical", False, "Do you have a current DOT medical card on file for every driver?", "Driver without a valid medical card"),
    ("insurance", False, "Is your liability insurance at or above the federal minimum for what you haul or the passengers you carry?", "Below minimum insurance"),
    ("defects", False, "When a driver reports a defect that makes a truck unsafe, is it always repaired before the truck runs again?", "Driver-reported defect not fixed"),
    ("oos", False, "If a truck has been put out of service at an inspection, was it repaired before it moved again?", "Driving a truck put out of service"),
    ("license", False, "Have you checked every driver's license and driving record, so you know each one is valid for the vehicle and not suspended or disqualified?", "Invalid, suspended or disqualified driver"),
    ("positive", True, "Is any driver who failed or refused a drug or alcohol test kept off the road until they finish the return-to-duty process?", "Using a driver after a failed or refused test"),
]
qs = "".join(f'''<fieldset class="q" data-id="{i}" data-cdl="{str(c).lower()}"><legend><span class="q-n">{n}</span>{t}</legend>
  <div class="segmented" role="radiogroup">
    <label><input type="radio" name="q-{i}" value="yes"> Yes</label><label><input type="radio" name="q-{i}" value="no"> No</label><label><input type="radio" name="q-{i}" value="unsure"> Not sure</label>
  </div></fieldset>''' for n, (i, c, t, _) in enumerate(QUESTIONS, 1))
CHECK_TOOL = f'''<section class="tool-card" aria-labelledby="chk-h">
  <h2 id="chk-h">Answer ten questions</h2>
  <form id="check-form" class="check-form" novalidate data-labels='{json.dumps({i: l for i, _, _, l in QUESTIONS})}'>
    <fieldset class="q q-gate"><legend>Do you or any of your drivers drive a vehicle that requires a CDL?</legend>
      <div class="segmented" role="radiogroup"><label><input type="radio" name="cdl" value="yes" checked> Yes</label><label><input type="radio" name="cdl" value="no"> No</label></div></fieldset>
    {qs}
    <button class="btn btn-primary" type="submit">See my results</button>
  </form>
  <div class="tool-result" id="check-result" hidden aria-live="polite"></div>
  <p class="fine">A self-check, not an audit result. It covers only the 16 automatic-fail rules, and answering yes to everything doesn't mean you'll pass. Nothing you answer is saved or sent.</p>
</section>'''
guide("audit-readiness-check.html",
  "New Entrant Safety Audit Readiness Check (Free) | FleetCleared",
  "Ten yes-or-no questions based on the 16 automatic-fail violations. See what to fix before your FMCSA safety audit. Free, nothing saved.",
  "Are you ready for your safety audit?",
  "Answer ten yes-or-no questions based on the 16 violations that fail a new entrant safety audit automatically. Every “no” or “not sure” is something to fix or confirm before the auditor looks.",
  [
    ("how", "How the check works", '''<p>Each question covers one or more of the 16 automatic-fail rules. Questions about drug and alcohol testing and CDLs only apply if you or your drivers need a CDL. A "yes" on every question doesn't guarantee a pass: auditors look at more than these 16 rules.</p>'''),
    ("next", "After the check", '''<p>Start with any "no" answers, because each one can fail the audit on its own. Then confirm the "not sure" answers by pulling the records. <a href="guide-new-entrant-safety-audit.html">The audit guide</a> lists what to have ready.</p>'''),
  ],
  [ECFR_321, FMCSA_FAQ],
  ["guide-automatic-fail-violations.html", "guide-new-entrant-safety-audit.html", "guide-failed-safety-audit.html", "guide-drug-alcohol-consortium.html"],
  "Free tool", "Audit readiness check", "",
  tool_html=CHECK_TOOL, scripts='\n<script src="assets/guides.js" defer></script>')

# ---------------------------------------------------------------- hub
def cards(group_names):
    return "".join(f'<a class="tour-card" href="{s}"><span class="variation">{g}</span><b>{c}</b><span>{b}</span></a>' for s, c, b, g in RELATED_INDEX if g in group_names)
REMIND = '''<section class="tool-card remind" aria-labelledby="remind-h" id="reminders">
  <h2 id="remind-h">Get a reminder before your deadlines</h2>
  <p>We'll email or text you before the deadlines you pick. That's all we send, and you can stop anytime.</p>
  <form id="remind-form" novalidate>
    <div class="form-grid">
      <div class="field"><label for="r-email">Email</label><input id="r-email" type="email" autocomplete="email"></div>
      <div class="field"><label for="r-phone">Mobile number for texts (optional)</label><input id="r-phone" type="tel" autocomplete="tel"></div>
      <div class="field full"><label for="r-usdot">USDOT number (for your MCS-150 month, optional)</label><input id="r-usdot" inputmode="numeric" autocomplete="off"></div>
    </div>
    <fieldset class="check-list"><legend>Remind me about</legend>
      <label class="check-inline"><input type="checkbox" name="d" value="ifta" checked> IFTA quarterly returns</label>
      <label class="check-inline"><input type="checkbox" name="d" value="ucr" checked> UCR registration</label>
      <label class="check-inline"><input type="checkbox" name="d" value="2290" checked> Form 2290</label>
      <label class="check-inline"><input type="checkbox" name="d" value="mcs150" checked> MCS-150 update</label>
      <label class="check-inline"><input type="checkbox" name="d" value="inspections"> Inspection weeks (Roadcheck, Brake Safety Week)</label>
    </fieldset>
    <label class="check-inline consent"><input type="checkbox" id="r-text-ok"> Text me reminders at the number above. Up to 4 automated texts a month. Message and data rates may apply. Reply STOP to cancel. Agreeing isn't required to use FleetCleared.</label>
    <p class="field-error" id="r-error" hidden></p>
    <button class="btn btn-primary" type="submit">Send me reminders</button>
  </form>
  <p class="notice" id="r-done" hidden>You're on the list. <span class="preview-label">Preview: reminders aren't connected yet, so nothing was saved.</span></p>
  <p class="fine">Reminders are a free courtesy. We can't guarantee every reminder arrives on time, so you stay responsible for your deadlines (see our <a href="terms.html#guides">terms</a>). We never share or sell your number or email, and we never pass it to consultants. See our <a href="privacy.html">privacy policy</a>.</p>
</section>'''
hub_ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Guides and free tools", "url": f"{SITE}/guides.html", "publisher": {"@id": f"{SITE}/#org"}}
write("guides.html", head("DOT Compliance Guides and Free Tools for Small Trucking Companies | FleetCleared",
  "Plain-language guides to the new entrant safety audit, drug and alcohol testing, CSA warning letters and filing deadlines, plus free tools. Sources linked on every page.",
  "guides.html", f'\n<script type="application/ld+json">{json.dumps(hub_ld)}</script>') + header("guides") + f'''<main class="wrap">
  <div class="page-head">
    <span class="eyebrow">Guides &amp; free tools</span>
    <h1>Plain answers to the compliance questions that keep carriers up at night</h1>
    <p class="lede">Written for small trucking companies, with the official source linked on every page. {"A directory of independent compliance consultants is coming in 2027." if LAUNCH else "When you'd rather hand it off, independent consultants are one click away."}</p>
  </div>
  <div class="tour">
    <section class="tour-section"><h2>New carriers and the safety audit</h2><div class="tour-grid">{cards(["New carriers"])}</div></section>
    <section class="tour-section"><h2>Free tools</h2><div class="tour-grid">{cards(["Free tool"])}</div></section>
    <section class="tour-section"><h2>Drug and alcohol testing</h2><div class="tour-grid">{cards(["Drug and alcohol"])}</div></section>
    <section class="tour-section"><h2>Trouble and deadlines</h2><div class="tour-grid">{cards(["Trouble", "Deadlines"])}</div></section>
  </div>
  {"" if LAUNCH else REMIND}
  {DISCLAIMER}
</main>
''' + guide_scripts('\n<script src="assets/guides.js" defer></script>'))
