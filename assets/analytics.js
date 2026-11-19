/* tarkkinnisvara.ee — consent banner + analytics.
   Nothing is loaded and no cookies are set until the visitor presses "Accept".
   The choice is kept in localStorage (key tk_consent: "yes" | "no"). */
(function () {
  var GA = 'G-1HJWYDG486';   // Google Analytics 4 (property tarkkinnisvara.ee)
  var PIXEL = '';            // Meta (Facebook) Pixel ID — set when the Business account is connected
  var KEY = 'tk_consent';
  var L = (document.documentElement.lang || 'et').slice(0, 2);
  var T = {
    et: { t: 'Kasutame nõusolekul küpsiseid külastuste ja päringute statistika jaoks. Ilma nõusolekuta statistikat ei koguta.', y: 'Nõustun', n: 'Keeldun', s: 'Küpsiste seaded', p: 'Privaatsus', l: 'privacy.html' },
    ru: { t: 'С вашего согласия мы используем cookies для статистики посещений и заявок. Без согласия статистика не собирается.', y: 'Принять', n: 'Отклонить', s: 'Настройки cookies', p: 'Конфиденциальность', l: 'privacy.html' },
    en: { t: 'With your consent we use cookies for visit and enquiry statistics. Without consent no statistics are collected.', y: 'Accept', n: 'Decline', s: 'Cookie settings', p: 'Privacy', l: 'privacy.html' }
  }[L] || null;
  if (!T) T = { t: '', y: '', n: '', s: '', p: '', l: 'privacy.html' };
  var loaded = false;

  function get() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function set(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  function load() {
    if (loaded) return; loaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    var s = document.createElement('script'); s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA; document.head.appendChild(s);
    gtag('js', new Date());
    gtag('config', GA, { anonymize_ip: true, allow_google_signals: false, allow_ad_personalization_signals: false });
    if (PIXEL) {
      !function (f, b, e, v, n, t, s) { if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
        if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = '2.0'; n.queue = []; t = b.createElement(e); t.async = !0; t.src = v;
        s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s); }(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');
      fbq('init', PIXEL); fbq('track', 'PageView');
    }
  }

  // events: safe no-op until consent
  window.tkTrack = function (name, params) {
    if (get() !== 'yes') return;
    try { if (window.gtag) gtag('event', name, params || {}); } catch (e) {}
    try { if (window.fbq && name === 'generate_lead') fbq('track', 'Lead'); } catch (e) {}
  };

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]'); if (!a) return;
    var h = a.getAttribute('href') || '';
    if (h.indexOf('tel:') === 0) tkTrack('phone_click', { link_url: h });
    else if (/kv\.ee\//.test(h)) tkTrack('kv_click', { link_url: h });
    else if (/calendly\.com/.test(h)) tkTrack('booking_click', { link_url: h });
  }, true);

  function remove() { var b = document.getElementById('tkc'); if (b) b.remove(); }
  function decide(v) { set(v); remove(); if (v === 'yes') load(); }

  function banner() {
    if (!T.t || document.getElementById('tkc')) return;
    var st = document.createElement('style');
    st.textContent = '#tkc{position:fixed;left:12px;right:12px;bottom:12px;z-index:9999;max-width:720px;margin:0 auto;background:#1c1917;color:#f4efe8;border-radius:14px;padding:14px 16px;box-shadow:0 8px 30px rgba(0,0,0,.28);font:14px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;display:flex;flex-wrap:wrap;gap:10px 14px;align-items:center}' +
      '#tkc p{margin:0;flex:1 1 280px}#tkc a{color:#f59e0b}#tkc .b{display:flex;gap:8px;flex:0 0 auto}' +
      '#tkc button{font:inherit;font-weight:600;border-radius:10px;padding:9px 16px;cursor:pointer;border:1px solid #f4efe8;background:transparent;color:#f4efe8;min-height:40px}' +
      '#tkc button.y{background:#f59e0b;border-color:#f59e0b;color:#1c1917}';
    var d = document.createElement('div'); d.id = 'tkc'; d.setAttribute('role', 'dialog'); d.setAttribute('aria-label', 'Cookies');
    d.innerHTML = '<p>' + T.t + ' <a href="' + T.l + '">' + T.p + '</a></p><div class="b"><button type="button" class="n">' + T.n + '</button><button type="button" class="y">' + T.y + '</button></div>';
    d.appendChild(st);
    d.querySelector('.y').onclick = function () { decide('yes'); };
    d.querySelector('.n').onclick = function () { decide('no'); };
    document.body.appendChild(d);
  }

  function settingsLink() {
    var f = document.querySelector('footer small') || document.querySelector('footer'); if (!f || !T.s || document.getElementById('tkc-set')) return;
    var a = document.createElement('a'); a.id = 'tkc-set'; a.href = '#'; a.textContent = T.s; a.style.marginLeft = '10px';
    a.onclick = function (e) { e.preventDefault(); banner(); };
    f.appendChild(a);
  }

  function init() {
    var c = get();
    if (c === 'yes') load(); else if (c !== 'no') banner();
    settingsLink();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
