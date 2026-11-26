/**
 * tarkkinnisvara.ee contact form -> e-mail to the office inbox, with spam filtering.
 * Deploy: Web app, Execute as "Me", Who has access "Anyone".
 * The site POSTs JSON as text/plain (no CORS preflight) and reads {ok:true|false}.
 *
 * Filtering (server side, so bots that post straight to the URL are covered too):
 *   score >= BLOCK      -> silently dropped (the sender still sees "ok"), kept in the "blocked" log
 *   score >= QUARANTINE -> delivered as "[SPAM?] ..." without Reply-To, so nothing real is lost
 *   otherwise           -> delivered normally with Reply-To = sender
 * Blocked and quarantined items are listed by showBlocked() (run it in the editor, see Executions log).
 */
var TO = 'OFFICE_INBOX@example.com'; // set the real recipient inside the Apps Script project (not stored in the public repo)
var MAX = {name: 120, phone: 40, email: 160, addr: 200, msg: 4000};
var BLOCK = 5, QUARANTINE = 3;
var BLOCK_DOMAINS = ['touristward.com', 'touristrise.com'];
var SPAM_RE = /(catalog(ue)?\b|backlink|\bseo\b|guest post|web ?design|traffic|crypto|bitcoin|casino|viagra|loan offer|work from home|link ?building|directory|add (you|it)|reminding you|write\s+"?yes"?|not interested\?|free of charge|commission|marketing (service|agency)|продвижени|раскрутк|трафик|каталог)/i;
var FREE_MAIL = /^(gmail|googlemail|hotmail|outlook|yahoo|icloud|me|mail|inbox|online|hot|neti|zone|tlu|msn|live)\.[a-z.]+$/i;

function clean_(v, n) { return String(v == null ? '' : v).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '').trim().slice(0, n); }

function domainOf_(email) { var m = /@([^@\s]+)$/.exec(email || ''); return m ? m[1].toLowerCase() : ''; }

// returns {score, why[]}
function score_(f) {
  var s = 0, why = [];
  function add(n, w) { s += n; why.push(w + '+' + n); }
  if (f.hp) add(10, 'honeypot');
  if (typeof f.t !== 'number') add(2, 'no-timer');
  else if (f.t < 3000) add(3, 'too-fast');
  var dom = domainOf_(f.email);
  if (dom && BLOCK_DOMAINS.indexOf(dom) >= 0) add(10, 'blocked-domain');
  var text = (f.msg + ' ' + f.addr + ' ' + f.name).toLowerCase();
  if (dom && !FREE_MAIL.test(dom) && text.indexOf(dom) >= 0) add(3, 'own-domain-in-text');
  var links = (f.msg.match(/(https?:\/\/[^\s]+|www\.[^\s]+|\b[a-z0-9-]{2,}\.(com|net|org|io|co|info|biz|xyz|online|site|top|shop|app|dev|ru|cn)\b)/gi) || []);
  links = links.filter(function (l) { var h = l.replace(/^https?:\/\//i, '').replace(/^www\./i, '').split(/[\/?#]/)[0].toLowerCase(); return !/\.ee$/.test(h); }); // .ee links (kv.ee, city24.ee ...) are fine
  if (links.length) add(3, 'links');
  if (SPAM_RE.test(f.msg)) add(3, 'spam-words');
  var digits = (f.phone || '').replace(/\D/g, '');
  if (digits) {
    if (/^(\d)\1+$/.test(digits) || /^10{5,}$/.test(digits) || digits === '1234567890' || digits === '123456789') add(3, 'fake-phone');
    else if (digits.length < 6 || digits.length > 15) add(2, 'odd-phone');
  }
  if (/^(1\s+)?main\s+street$|^test$|^n\/?a$|^-+$|^asdf/i.test(f.addr || '')) add(2, 'fake-address');
  if (f.msg.length > 60 && !/[а-яёõäöüšž]/i.test(f.msg) && (f.msg.match(/\b(the|and|you|your|we|our|to|is)\b/gi) || []).length >= 4) add(1, 'english-only');
  return {score: s, why: why};
}

function remember_(entry) {
  try {
    var p = PropertiesService.getScriptProperties(), arr = JSON.parse(p.getProperty('blocked') || '[]');
    arr.push(entry); if (arr.length > 40) arr = arr.slice(-40);
    p.setProperty('blocked', JSON.stringify(arr));
  } catch (e) {}
}

function doPost(e) {
  try {
    var d = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    var f = {name: clean_(d.name, MAX.name), phone: clean_(d.phone, MAX.phone), email: clean_(d.email, MAX.email),
             addr: clean_(d.addr, MAX.addr), msg: clean_(d.msg, MAX.msg), lang: clean_(d.lang, 5), page: clean_(d.page, 300),
             hp: clean_(d.hp, 50), t: typeof d.t === 'number' ? d.t : null};
    if (!f.name || !(f.phone || f.email)) return out_({ok: false, error: 'missing'});
    if (f.email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(f.email)) return out_({ok: false, error: 'email'});
    var cache = CacheService.getScriptCache();
    var r = score_(f);
    // the same address more than 3 times a day counts as flooding
    if (f.email) {
      var ek = 'e' + Utilities.base64EncodeWebSafe(f.email.toLowerCase()).slice(0, 80), en = parseInt(cache.get(ek) || '0', 10);
      cache.put(ek, String(en + 1), 21600);
      if (en >= 3) { r.score += 5; r.why.push('flood+5'); }
    }
    var info = {ts: Utilities.formatDate(new Date(), 'Europe/Tallinn', 'dd.MM.yyyy HH:mm'), score: r.score, why: r.why.join(','), name: f.name, email: f.email};
    if (r.score >= BLOCK) { remember_(info); console.log('BLOCKED ' + JSON.stringify(info)); return out_({ok: true}); }
    // simple rate limit: max 20 delivered messages per hour
    var key = 'n' + Utilities.formatDate(new Date(), 'UTC', 'yyyyMMddHH'), n = parseInt(cache.get(key) || '0', 10);
    if (n >= 20) return out_({ok: false, error: 'rate'});
    cache.put(key, String(n + 1), 3700);
    var q = r.score >= QUARANTINE;
    var body = (q ? 'KAHTLANE PÄRING (spämmi hinne ' + r.score + ': ' + r.why.join(', ') + '). Ära ava linke ega vasta, kui ei tunne saatjat.\n\n' : '') +
      'Uus päring kodulehelt tarkkinnisvara.ee\n\n' +
      'Nimi: ' + f.name + '\nTelefon: ' + f.phone + '\nE-post: ' + f.email + '\nKorteri aadress: ' + f.addr + '\n\nSõnum:\n' + f.msg +
      '\n\nKeel: ' + f.lang + '\nLeht: ' + f.page + '\nSaadetud: ' + Utilities.formatDate(new Date(), 'Europe/Tallinn', 'dd.MM.yyyy HH:mm');
    var opts = {name: 'tarkkinnisvara.ee'};
    if (f.email && !q) opts.replyTo = f.email;
    if (q) { remember_(info); console.log('QUARANTINED ' + JSON.stringify(info)); }
    MailApp.sendEmail(TO, (q ? '[SPAM?] ' : '') + '[tarkkinnisvara.ee] Uus päring: ' + f.name, body, opts);
    return out_({ok: true});
  } catch (err) {
    return out_({ok: false, error: 'server'});
  }
}

// run in the editor to see what was blocked or quarantined (View > Executions / Logs)
function showBlocked() { console.log(PropertiesService.getScriptProperties().getProperty('blocked') || '[]'); }

function doGet() { return out_({ok: true, service: 'tarkkinnisvara.ee form'}); }

function out_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
