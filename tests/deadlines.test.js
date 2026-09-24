const test = require('node:test');
const assert = require('node:assert/strict');
const D = require('../assets/deadlines.js');

const day = (y, m, d) => new Date(y, m - 1, d);

test('last digit picks the month; 0 means October', () => {
  assert.equal(D.mcs150Schedule('1234561').month, 'January');
  assert.equal(D.mcs150Schedule('1234569').month, 'September');
  assert.equal(D.mcs150Schedule('1234560').month, 'October');
});

test('next-to-last digit picks odd or even years', () => {
  assert.equal(D.mcs150Schedule('1234531').oddYears, true);  // 3 is odd
  assert.equal(D.mcs150Schedule('1234541').oddYears, false); // 4 is even
  assert.equal(D.mcs150Schedule('7').oddYears, false);       // one digit counts as even
});

test('finds the next due month from a given day', () => {
  // ...45: month May, even years. From Sep 24 2026, May 2026 has passed, so next is May 2028.
  let r = D.mcs150NextDue('1234545', day(2026, 9, 24));
  assert.equal(r.year, 2028); assert.equal(r.month, 'May');
  // ...39: September, odd years. From Sep 2026 the next odd year is 2027.
  r = D.mcs150NextDue('1234539', day(2026, 9, 24));
  assert.equal(r.year, 2027); assert.equal(r.month, 'September');
  // ...40: October, even years. From Sep 24 2026 that is next month.
  r = D.mcs150NextDue('1234540', day(2026, 9, 24));
  assert.equal(r.year, 2026); assert.equal(r.month, 'October'); assert.equal(r.monthsAway, 1);
});

test('the due month itself still counts until it ends, and due date is the last day', () => {
  const r = D.mcs150NextDue('1234549', day(2026, 9, 30)); // September, even years
  assert.equal(r.year, 2026); assert.equal(r.thisMonth, true);
  assert.equal(r.dueBy.getDate(), 30);
  assert.equal(D.mcs150NextDue('1234522', day(2026, 1, 5)).dueBy.getDate(), 28); // February 2026
});

test('accepts common ways of typing the number and rejects junk', () => {
  assert.equal(D.cleanUsdot('USDOT #1,234,567'), '1234567');
  assert.equal(D.cleanUsdot(' 1234567 '), '1234567');
  assert.throws(() => D.cleanUsdot('abc'));
  assert.throws(() => D.cleanUsdot('123456789')); // 9 digits
  assert.throws(() => D.cleanUsdot('0'));
});
