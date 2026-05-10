/* Corvela International — interactions */

// Mobile nav toggle
const toggle = document.querySelector('.nav-toggle');
const navLinks = document.querySelector('.nav-links');

toggle?.addEventListener('click', () => {
  const expanded = toggle.getAttribute('aria-expanded') === 'true';
  toggle.setAttribute('aria-expanded', String(!expanded));
  navLinks.classList.toggle('open', !expanded);
});

// Close nav on link click
navLinks?.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => {
    toggle.setAttribute('aria-expanded', 'false');
    navLinks.classList.remove('open');
  });
});

// Nav shadow on scroll
const header = document.querySelector('.nav-header');
const onScroll = () => header?.classList.toggle('scrolled', window.scrollY > 40);
window.addEventListener('scroll', onScroll, { passive: true });
onScroll();

// Contact form — basic feedback
const form = document.querySelector('.contact-form');
form?.addEventListener('submit', e => {
  e.preventDefault();
  const btn = form.querySelector('button[type="submit"]');
  btn.textContent = 'Enquiry Sent \u2713';
  btn.style.background = 'var(--gold-dark)';
  btn.style.color = 'var(--white)';
  btn.disabled = true;
  form.querySelectorAll('input, textarea').forEach(el => el.value = '');
  setTimeout(() => {
    btn.textContent = 'Send Enquiry';
    btn.style.background = '';
    btn.style.color = '';
    btn.disabled = false;
  }, 4000);
});

// =============================================
// FIND YOUR PLAN — step-by-step widget
// =============================================
(function () {
  const QUESTIONS = [
    { key: 'Trip Type',    label: 'Trip Type' },
    { key: 'Region',       label: 'Region' },
    { key: 'Age',          label: 'Age' },
    { key: 'USA Coverage', label: 'USA Coverage' },
    { key: 'Budget',       label: 'Monthly Budget' },
    { key: 'Priority',     label: 'Top Priority' },
  ];

  let current = 1;
  const answers = {};

  const steps        = document.querySelectorAll('.fp-step');
  const progressFill = document.getElementById('fpProgressFill');
  const stepCounter  = document.getElementById('fpStepCounter');
  const backBtn      = document.getElementById('fpBack');
  const ageInput     = document.getElementById('fpAge');
  const ageNextBtn   = document.getElementById('fpAgeNext');
  const summaryEl    = document.getElementById('fpSummary');
  const restartBtn   = document.getElementById('fpRestart');
  const progressBar  = document.querySelector('.fp-progress');

  if (!steps.length) return;

  function updateProgress(step) {
    if (progressFill) progressFill.style.width = (step <= 6 ? (step / 6 * 100) : 100) + '%';
    if (stepCounter)  stepCounter.textContent   = step <= 6 ? `Step ${step} of 6` : 'Complete';
    if (progressBar)  progressBar.setAttribute('aria-valuenow', step);
  }

  function showStep(next) {
    const currentEl = document.querySelector(`.fp-step[data-step="${current}"]`);
    const nextEl    = document.querySelector(`.fp-step[data-step="${next}"]`);
    if (!nextEl) return;

    if (currentEl) {
      currentEl.classList.add('exit');
      setTimeout(() => currentEl.classList.remove('active', 'exit'), 220);
    }

    setTimeout(() => {
      nextEl.classList.add('active');
      current = next;
      updateProgress(current);
      backBtn.hidden = (current <= 1 || current === 7);
    }, 230);
  }

  // --------------------------------------------------
  // Carrier data
  // --------------------------------------------------
  const CARRIERS = {
    cigna: {
      name: 'Cigna Global',
      tagline: 'Premium worldwide coverage with direct billing',
      quoteUrl: 'https://www.cignaglobal.com/partnerQuote/tool?AffinityPartner=89c121c448a3570e50e3a102fb67eb85&utm_source=broker&utm_medium=online&utm_campaign=brokerQuickQuote&utm_content=default',
      strengths: ['Largest global hospital network', 'Direct billing at 40,000+ facilities', 'USA coverage available', '24/7 US-based support', 'Annually renewable expat plans'],
      bestFor: 'Long-term expats and those needing comprehensive, hassle-free coverage',
      priceRange: '$150–$500+/mo',
    },
    img: {
      name: 'IMG Global Medical',
      tagline: 'Flexible, cost-effective plans for travelers and expats',
      quoteUrl: 'https://producer.imglobal.com/international-insurance-plans.aspx?imgac=56427',
      strengths: ['Competitive pricing', 'Flexible plan design', 'Strong short-term travel plans', 'Optional USA coverage add-on', 'Fast claims processing'],
      bestFor: 'Short-term travelers and budget-conscious expats who want solid core coverage',
      priceRange: '$50–$250/mo',
    },
  };

  // --------------------------------------------------
  // Ranking logic — score both carriers, pick winner
  // --------------------------------------------------
  function scoreCarriers(a) {
    let cignaScore = 0;
    let imgScore   = 0;

    // Trip type
    if (a['Trip Type'] === 'Long-Term Expat')    cignaScore += 3;
    if (a['Trip Type'] === 'Short-Term Travel')  imgScore   += 3;

    // USA coverage needed
    if (a['USA Coverage'] === 'Yes')             cignaScore += 2;
    if (a['USA Coverage'] === 'No')              imgScore   += 1;

    // Budget
    if (a['Budget'] === 'Under $100')            imgScore   += 3;
    if (a['Budget'] === '$100–$200')             imgScore   += 2;
    if (a['Budget'] === '$200–$400')             cignaScore += 1;
    if (a['Budget'] === '$400+')                 cignaScore += 3;

    // Priority
    if (a['Priority'] === 'Lowest Price')        imgScore   += 2;
    if (a['Priority'] === 'Broadest Coverage')   cignaScore += 3;
    if (a['Priority'] === 'US-Based Support')    cignaScore += 2;

    // Region — Cigna stronger in Europe/Middle East; IMG competitive in Latin America/Asia
    if (a['Region'] === 'Europe')                cignaScore += 1;
    if (a['Region'] === 'Middle East')           cignaScore += 2;
    if (a['Region'] === 'Latin America')         imgScore   += 1;
    if (a['Region'] === 'Asia')                  imgScore   += 1;

    return { cigna: cignaScore, img: imgScore };
  }

  // --------------------------------------------------
  // Build dual-carrier result cards
  // --------------------------------------------------
  function buildRecommendation() {
    const scores  = scoreCarriers(answers);
    const winner  = scores.cigna >= scores.img ? 'cigna' : 'img';
    const runner  = winner === 'cigna' ? 'img' : 'cigna';

    const card = document.getElementById('fpRecCard');
    if (!card) return;

    card.innerHTML = `
      <div class="fp-compare-grid">
        ${buildCarrierCard(winner, true, answers)}
        ${buildCarrierCard(runner, false, answers)}
      </div>
      <p class="fp-compare-note">Both plans are available through Corvela at no extra cost. We're happy to walk you through the differences — <a href="#contact">contact us</a> anytime.</p>
    `;

    card.removeAttribute('hidden');
  }

  function buildCarrierCard(key, isBestMatch, a) {
    const c = CARRIERS[key];
    const age = a['Age'] ? parseInt(a['Age']) : null;
    const why = buildWhy(key, a);

    return `
      <div class="fp-carrier-card ${isBestMatch ? 'fp-carrier-card--best' : 'fp-carrier-card--alt'}">
        <div class="fp-carrier-header">
          <span class="fp-carrier-badge ${isBestMatch ? 'fp-carrier-badge--best' : 'fp-carrier-badge--alt'}">
            ${isBestMatch ? '★ Best Match' : 'Also Consider'}
          </span>
          <h3 class="fp-carrier-name">${c.name}</h3>
          <p class="fp-carrier-tagline">${c.tagline}</p>
          <p class="fp-carrier-price">${c.priceRange}</p>
        </div>
        <p class="fp-carrier-why">${why}</p>
        <ul class="fp-carrier-strengths">
          ${c.strengths.map(s => `<li>${s}</li>`).join('')}
        </ul>
        <a href="${c.quoteUrl}" target="_blank" rel="noopener"
           class="btn ${isBestMatch ? 'btn-primary' : 'btn-outline-dark'} fp-carrier-cta">
          Get a ${c.name} Quote →
        </a>
      </div>
    `;
  }

  function buildWhy(key, a) {
    const isExpat      = a['Trip Type'] === 'Long-Term Expat';
    const needsUSA     = a['USA Coverage'] === 'Yes';
    const region       = a['Region'] || 'your destination';
    const budget       = a['Budget'] || 'your budget';
    const priority     = a['Priority'];

    if (key === 'cigna') {
      if (isExpat && needsUSA)
        return `Cigna Global is the strongest fit for long-term expats who need to stay covered during visits back to the US. Their USA tier is comprehensive and designed exactly for this situation.`;
      if (isExpat)
        return `For long-term expats in ${region}, Cigna's annually renewable plans provide the continuity and network depth you need when a foreign country becomes your home base.`;
      if (priority === 'Broadest Coverage')
        return `Cigna offers the widest hospital network in ${region} with direct billing at most major facilities — meaning fewer out-of-pocket expenses and less paperwork when you need care.`;
      if (priority === 'US-Based Support')
        return `Cigna's 24/7 US-based support line handles pre-authorizations, claims, and hospital coordination — a significant advantage when navigating healthcare abroad.`;
      return `Cigna Global provides comprehensive coverage in ${region} with a strong network and reliable claims support. A dependable choice given your profile.`;
    } else {
      if (!isExpat && budget === 'Under $100')
        return `IMG's short-term travel plans deliver strong emergency and hospitalization coverage at rates that fit a tight budget — often the best value in the market for trips under 6 months.`;
      if (!isExpat)
        return `For short-term travel in ${region}, IMG's Patriot series is purpose-built for your situation — solid core coverage without paying for the long-term expat features you don't need.`;
      if (priority === 'Lowest Price')
        return `IMG consistently offers lower premiums than comparable plans, with the ability to customize your deductible and coverage modules to keep costs within ${budget}.`;
      return `IMG Global Medical offers flexible, competitively priced coverage for ${region}. Their customizable plan structure means you pay for what you actually need.`;
    }
  }

  function buildSummary() {
    if (!summaryEl) return;
    summaryEl.innerHTML = QUESTIONS.map(q =>
      `<div class="fp-summary-row">
        <span class="fp-summary-label">${q.label}</span>
        <span class="fp-summary-value">${answers[q.key] || '—'}</span>
      </div>`
    ).join('');
  }

  // Option button clicks
  document.querySelectorAll('.fp-opt').forEach(btn => {
    btn.addEventListener('click', () => {
      const step = parseInt(btn.closest('.fp-step').dataset.step);
      const key  = QUESTIONS[step - 1].key;
      answers[key] = btn.dataset.value;

      btn.closest('.fp-options').querySelectorAll('.fp-opt').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');

      const next = step < 6 ? step + 1 : 7;
      setTimeout(() => {
        if (next === 7) { buildSummary(); buildRecommendation(); }
        showStep(next);
      }, 180);
    });
  });

  // Age input
  ageInput?.addEventListener('input', () => {
    const val = parseInt(ageInput.value);
    if (ageNextBtn) ageNextBtn.disabled = !(val >= 1 && val <= 120);
  });

  ageNextBtn?.addEventListener('click', () => {
    answers['Age'] = ageInput.value + ' years old';
    showStep(4);
  });

  // Back
  backBtn?.addEventListener('click', () => {
    if (current > 1) showStep(current - 1);
  });

  // Restart
  restartBtn?.addEventListener('click', () => {
    Object.keys(answers).forEach(k => delete answers[k]);
    if (ageInput)    ageInput.value = '';
    if (ageNextBtn)  ageNextBtn.disabled = true;
    document.querySelectorAll('.fp-opt').forEach(b => b.classList.remove('selected'));
    const recCard = document.getElementById('fpRecCard');
    if (recCard) { recCard.setAttribute('hidden', ''); recCard.innerHTML = ''; }
    document.querySelectorAll('.fp-step').forEach(s => s.classList.remove('active', 'exit'));
    current = 0;
    showStep(1);
  });

  updateProgress(1);
})();

// Scroll-in animation
const animItems = document.querySelectorAll(
  '.service-card, .why-card, .stat-item, .contact-detail-item'
);
if ('IntersectionObserver' in window) {
  const io = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  animItems.forEach((el, i) => {
    el.style.cssText += `opacity:0; transform:translateY(24px); transition: opacity 0.5s ease ${i * 0.06}s, transform 0.5s ease ${i * 0.06}s, box-shadow 0.25s ease, border-color 0.25s ease`;
    io.observe(el);
  });
}
