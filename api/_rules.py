# Python port of assets/rules.js pricing/decision logic. assets/rules.js is the spec (and what
# tests/rules.test.js checks); keep both in sync by hand. Leading underscore: Vercel doesn't turn
# this into its own route, so other api/*.py files can import it as a shared helper.

PRICING_TIERS = [
    (1, 2, 30),
    (3, 10, 45),
    (11, float("inf"), 65),
]
PRICING_FLOOR = 25
PRICING_CEILING = 90


def tier_for(fleet_size):
    n = fleet_size
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("Fleet size must be a whole number of trucks, 1 or more")
    for lo, hi, price in PRICING_TIERS:
        if lo <= n <= hi:
            return (lo, hi, price)
    raise ValueError("No matching pricing tier")


def lead_price(fleet_size):
    return tier_for(fleet_size)[2]


def decide_lead(account, fleet_size):
    """account: {freeLeadUsedByBusiness, cardOnFile, leadsThisMonth, monthlyCap (None = no limit)}.
    Returns {action: 'deliver'|'decline'|'hold', charge, note} -- mirrors assets/rules.js decideLead()."""
    price = lead_price(fleet_size)
    if not account.get("freeLeadUsedByBusiness"):
        return {"action": "deliver", "charge": 0, "note": "First lead for this business: free"}
    cap = account.get("monthlyCap")
    if cap is not None and account.get("leadsThisMonth", 0) >= cap:
        return {"action": "decline", "charge": 0, "note": "Monthly lead limit reached; tell the carrier this consultant is unavailable"}
    if not account.get("cardOnFile"):
        return {"action": "hold", "charge": 0, "note": "No card on file; hold up to 48 hours and ask the consultant to add one"}
    return {"action": "deliver", "charge": price, "note": f"Charged ${price}"}


if __name__ == "__main__":
    # Lightweight parity check against the cases in tests/rules.test.js. Run with: python3 api/_rules.py
    assert lead_price(1) == 30 and lead_price(2) == 30
    assert lead_price(3) == 45 and lead_price(10) == 45
    assert lead_price(11) == 65 and lead_price(400) == 65
    for bad in (0, -3, 2.5, "abc", None):
        try:
            lead_price(bad)
            raise AssertionError(f"expected lead_price({bad!r}) to raise")
        except ValueError:
            pass
    d = decide_lead({"freeLeadUsedByBusiness": False, "cardOnFile": False, "leadsThisMonth": 0, "monthlyCap": None}, 12)
    assert (d["action"], d["charge"]) == ("deliver", 0)
    d = decide_lead({"freeLeadUsedByBusiness": True, "cardOnFile": False, "leadsThisMonth": 0, "monthlyCap": None}, 5)
    assert (d["action"], d["charge"]) == ("hold", 0)
    d = decide_lead({"freeLeadUsedByBusiness": True, "cardOnFile": True, "leadsThisMonth": 3, "monthlyCap": 10}, 5)
    assert (d["action"], d["charge"]) == ("deliver", 45)
    d = decide_lead({"freeLeadUsedByBusiness": True, "cardOnFile": True, "leadsThisMonth": 10, "monthlyCap": 10}, 5)
    assert (d["action"], d["charge"]) == ("decline", 0)
    print("ok: api/_rules.py matches tests/rules.test.js")
