const test = require('node:test');
const assert = require('node:assert/strict');
const H = require('../assets/hours.js');
const R = require('../assets/rules.js');

const weekdays = (h, sat = null) => [h, h, h, h, h, sat, null];
const hours = weekdays('7:00 AM – 5:00 PM', '8:00 AM – 12:00 PM');
// Wednesday Sep 23 2026. Times are given in UTC; Central Time is UTC-5 in September.
const at = (iso) => new Date(iso);

test('reads 12-hour times, including noon and midnight edges', () => {
  assert.deepEqual(H.parseRange('7:00 AM – 5:00 PM'), [420, 1020]);
  assert.deepEqual(H.parseRange('8:00 AM - 12:00 PM'), [480, 720]);
  assert.equal(H.toMinutes('12:00 AM'), 0);
  assert.equal(H.parseRange(null), null);
  assert.throws(() => H.toMinutes('7am'));
});

test('open during hours, using the consultant time zone, not the visitor\'s', () => {
  const s = H.openStatus(hours, 'Central Time', at('2026-09-23T15:00:00Z')); // 10:00 AM Central
  assert.equal(s.open, true);
  assert.equal(s.text, 'Open now · until 5:00 PM');
  const east = H.openStatus(weekdays('8:00 AM – 5:00 PM'), 'Eastern Time', at('2026-09-23T12:30:00Z')); // 8:30 AM Eastern
  assert.equal(east.open, true);
});

test('closing time itself counts as closed', () => {
  const s = H.openStatus(hours, 'Central Time', at('2026-09-23T22:00:00Z')); // 5:00 PM Central
  assert.equal(s.open, false);
  assert.equal(s.text, 'Closed · opens tomorrow at 7:00 AM');
});

test('before opening says today', () => {
  const s = H.openStatus(hours, 'Central Time', at('2026-09-23T10:00:00Z')); // 5:00 AM Central
  assert.equal(s.text, 'Closed · opens today at 7:00 AM');
});

test('Saturday evening skips closed Sunday to Monday', () => {
  const s = H.openStatus(hours, 'Central Time', at('2026-09-26T23:00:00Z')); // Sat 6:00 PM Central
  assert.equal(s.text, 'Closed · opens Monday at 7:00 AM');
});

test('no hours at all is handled', () => {
  assert.equal(H.openStatus([null, null, null, null, null, null, null], 'Central Time', at('2026-09-23T15:00:00Z')).text, 'Hours not listed');
});

test('monthly estimate uses the real pricing decision, free lead first', () => {
  assert.deepEqual(R.estimateMonthly({ leadsPerMonth: 5, fleetSize: 3, monthlyCap: null, freeLeadAvailable: true }), { delivered: 5, declined: 0, total: 180 });
  assert.deepEqual(R.estimateMonthly({ leadsPerMonth: 5, fleetSize: 3, monthlyCap: null, freeLeadAvailable: false }), { delivered: 5, declined: 0, total: 225 });
});

test('monthly estimate stops charging at the cap', () => {
  assert.deepEqual(R.estimateMonthly({ leadsPerMonth: 12, fleetSize: 1, monthlyCap: 10 }), { delivered: 10, declined: 2, total: 300 });
  assert.deepEqual(R.estimateMonthly({ leadsPerMonth: 0, fleetSize: 1 }), { delivered: 0, declined: 0, total: 0 });
  assert.throws(() => R.estimateMonthly({ leadsPerMonth: -1, fleetSize: 1 }));
});
