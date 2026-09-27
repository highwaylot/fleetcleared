// Consultant card-setup page (add-card.html). The consultant id lives in the URL hash, same
// pattern consultant.html already uses for its profile deep links. Card details go straight to
// Stripe via Elements; this script never sees or handles the raw card number.
(function () {
  const id = location.hash.slice(1);
  const form = document.getElementById('ac-form');
  const errorEl = document.getElementById('ac-error');
  const submitBtn = document.getElementById('ac-submit');
  if (!id || !form) return;

  function showError(msg) {
    errorEl.textContent = msg;
    errorEl.hidden = !msg;
  }

  fetch(`/api/consultant_card_setup?id=${encodeURIComponent(id)}`)
    .then(res => res.json())
    .then(data => {
      if (!data.ok) { showError("We couldn't find that listing. Check the link from your approval email."); form.hidden = true; return; }
      if (data.name) document.getElementById('ac-name').textContent = `Add a payment method, ${data.name}`;
      document.getElementById('ac-card').hidden = !data.hasCard;
    })
    .catch(() => showError('Something went wrong loading this page. Refresh and try again.'));

  let stripe, elements, card;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    showError('');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Saving...';
    try {
      const setupRes = await fetch('/api/consultant_card_setup', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id }),
      });
      const setup = await setupRes.json();
      if (!setup.ok) throw new Error(setup.error || 'Could not start card setup.');

      if (!stripe) {
        stripe = Stripe(setup.publishableKey);
        elements = stripe.elements();
        card = elements.create('card');
        card.mount('#ac-element');
      }

      const result = await stripe.confirmCardSetup(setup.clientSecret, { payment_method: { card } });
      if (result.error) throw new Error(result.error.message || 'Your card was not saved.');

      form.hidden = true;
      document.getElementById('ac-done').hidden = false;
    } catch (err) {
      showError(err.message || 'Something went wrong. Try again.');
      submitBtn.disabled = false;
      submitBtn.textContent = 'Save card';
    }
  });
})();
