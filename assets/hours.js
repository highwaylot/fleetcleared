// Opening-hours logic for consultant profiles: "Open now" / "Closed" in the consultant's own time zone.
// Runs in the browser (window.FCHours) and in Node (require) so it is tested like the business rules.
(function (root) {
  const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  const ZONES = { 'Eastern Time': 'America/New_York', 'Central Time': 'America/Chicago', 'Mountain Time': 'America/Denver', 'Pacific Time': 'America/Los_Angeles', 'Alaska Time': 'America/Anchorage', 'Hawaii Time': 'Pacific/Honolulu' };

  // "7:00 AM" -> minutes after midnight
  function toMinutes(t) {
    const m = String(t).trim().match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i);
    if (!m) throw new Error(`Unreadable time: ${t}`);
    let h = Number(m[1]) % 12;
    if (m[3].toUpperCase() === 'PM') h += 12;
    return h * 60 + Number(m[2]);
  }
  // "7:00 AM – 5:00 PM" -> [420, 1020]; null or empty -> null (closed)
  function parseRange(range) {
    if (!range) return null;
    const [a, b] = String(range).split(/\s*[–-]\s*/);
    return [toMinutes(a), toMinutes(b)];
  }
  const label = (range) => String(range).split(/\s*[–-]\s*/);

  // Day of week (0 = Monday) and minutes after midnight in the consultant's time zone.
  function localNow(tzLabel, now = new Date()) {
    const timeZone = ZONES[tzLabel] || 'America/Chicago';
    const parts = Object.fromEntries(new Intl.DateTimeFormat('en-US', { timeZone, weekday: 'long', hour: 'numeric', minute: 'numeric', hourCycle: 'h23' })
      .formatToParts(now).map((p) => [p.type, p.value]));
    return { day: DAY_NAMES.indexOf(parts.weekday), minutes: Number(parts.hour) * 60 + Number(parts.minute) };
  }

  // hours: 7 entries, Monday first, each "7:00 AM – 5:00 PM" or null.
  function openStatus(hours, tzLabel, now = new Date()) {
    const { day, minutes } = localNow(tzLabel, now);
    const today = parseRange(hours[day]);
    if (today && minutes >= today[0] && minutes < today[1]) {
      return { open: true, today: day, text: `Open now · until ${label(hours[day])[1]}` };
    }
    if (today && minutes < today[0]) {
      return { open: false, today: day, text: `Closed · opens today at ${label(hours[day])[0]}` };
    }
    for (let i = 1; i <= 7; i++) {
      const d = (day + i) % 7;
      if (hours[d]) {
        const when = i === 1 ? 'tomorrow' : DAY_NAMES[d];
        return { open: false, today: day, text: `Closed · opens ${when} at ${label(hours[d])[0]}` };
      }
    }
    return { open: false, today: day, text: 'Hours not listed' };
  }

  const api = { parseRange, toMinutes, localNow, openStatus, ZONES };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.FCHours = api;
})(typeof window !== 'undefined' ? window : globalThis);
