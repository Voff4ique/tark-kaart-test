/**
 * tarkkinnisvara.ee contact form -> e-mail to the office inbox.
 * Deploy: Web app, Execute as "Me", Who has access "Anyone".
 * The site POSTs JSON as text/plain (no CORS preflight) and reads {ok:true|false}.
 */
var TO = 'office.kinnisvara@gmail.com';
var MAX = {name: 120, phone: 40, email: 160, addr: 200, msg: 4000};

function clean_(v, n) { return String(v == null ? '' : v).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '').trim().slice(0, n); }

function doPost(e) {
  try {
    var d = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    var name = clean_(d.name, MAX.name), phone = clean_(d.phone, MAX.phone), email = clean_(d.email, MAX.email),
        addr = clean_(d.addr, MAX.addr), msg = clean_(d.msg, MAX.msg), lang = clean_(d.lang, 5), page = clean_(d.page, 300);
    if (!name || !(phone || email)) return out_({ok: false, error: 'missing'});
    if (email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return out_({ok: false, error: 'email'});
    // simple rate limit: max 20 messages per hour
    var cache = CacheService.getScriptCache(), key = 'n' + Utilities.formatDate(new Date(), 'UTC', 'yyyyMMddHH');
    var n = parseInt(cache.get(key) || '0', 10);
    if (n >= 20) return out_({ok: false, error: 'rate'});
    cache.put(key, String(n + 1), 3700);
    var body = 'Uus päring kodulehelt tarkkinnisvara.ee\n\n' +
      'Nimi: ' + name + '\nTelefon: ' + phone + '\nE-post: ' + email + '\nKorteri aadress: ' + addr + '\n\nSõnum:\n' + msg +
      '\n\nKeel: ' + lang + '\nLeht: ' + page + '\nSaadetud: ' + Utilities.formatDate(new Date(), 'Europe/Tallinn', 'dd.MM.yyyy HH:mm');
    var opts = {name: 'tarkkinnisvara.ee'};
    if (email) opts.replyTo = email;
    MailApp.sendEmail(TO, '[tarkkinnisvara.ee] Uus päring: ' + name, body, opts);
    return out_({ok: true});
  } catch (err) {
    return out_({ok: false, error: 'server'});
  }
}

function doGet() { return out_({ok: true, service: 'tarkkinnisvara.ee form'}); }

function out_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
