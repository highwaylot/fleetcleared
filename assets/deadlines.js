// Filing-deadline math for the free tools on the guide pages.
// Runs in the browser (window.FCDeadlines) and in Node (require) so it is tested like the business rules.
(function (root) {
  const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

  // "USDOT 1234567", "1,234,567" -> "1234567". Throws on anything that isn't 1–8 digits.
  function cleanUsdot(input) {
    const d = String(input || '').replace(/usdot|dot|#|no\.?|[\s,.-]/gi, '');
    if (!/^\d{1,8}$/.test(d) || Number(d) === 0) throw new Error('Enter your USDOT number: digits only, up to 8 of them');
    return d;
  }

  // MCS-150 biennial update schedule (49 CFR 390.19):
  // last digit sets the month (1 = January … 9 = September, 0 = October);
  // next-to-last digit sets the year: odd digit = odd-numbered years, even digit = even-numbered years.
  // A one-digit number has no next-to-last digit and counts as even.
  function mcs150Schedule(usdot) {
    const d = cleanUsdot(usdot);
    const last = Number(d[d.length - 1]);
    const tens = d.length > 1 ? Number(d[d.length - 2]) : 0;
    const monthIndex = last === 0 ? 9 : last - 1;
    return { usdot: d, monthIndex, month: MONTHS[monthIndex], oddYears: tens % 2 === 1 };
  }

  // Next filing month on or after `today`: the filing is due by the end of that month.
  function mcs150NextDue(usdot, today = new Date()) {
    const s = mcs150Schedule(usdot);
    let year = today.getFullYear();
    const parityOk = (y) => (y % 2 === 1) === s.oddYears;
    while (!parityOk(year) || year * 12 + s.monthIndex < today.getFullYear() * 12 + today.getMonth()) year++;
    const dueBy = new Date(year, s.monthIndex + 1, 0); // last day of the month
    const monthsAway = (year * 12 + s.monthIndex) - (today.getFullYear() * 12 + today.getMonth());
    return { ...s, year, dueBy, monthsAway, thisMonth: monthsAway === 0 };
  }

  const api = { cleanUsdot, mcs150Schedule, mcs150NextDue, MONTHS };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.FCDeadlines = api;
})(typeof window !== 'undefined' ? window : globalThis);
