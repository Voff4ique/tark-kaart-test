# -*- coding: utf-8 -*-
"""All Tark-owned copy that the build adds on top of the page sources (ET / RU / EN)."""

META = {
 'index': {
  'et': ("Tark Kinnisvara — korterite ost, renoveerimine ja müük Tallinnas",
         "Ostame remonti vajavad ja pärandiks saadud korterid Tallinnas, hindame 24 tunniga. Renoveerime ja müüme valmis kodud. Vaata meie objekte kaardil."),
  'ru': ("Tark Kinnisvara — выкуп, ремонт и продажа квартир в Таллине",
         "Выкупаем квартиры, требующие ремонта, и унаследованные квартиры в Таллине, оценка за 24 часа. Ремонтируем и продаём готовые дома. Наши объекты на карте."),
  'en': ("Tark Kinnisvara — we buy, renovate and sell flats in Tallinn",
         "We buy flats needing renovation and inherited flats in Tallinn, valuation within 24 hours. We renovate and sell move-in-ready homes. See our projects on the map."),
 },
 'myygil': {
  'et': ("Müügil olevad korterid Tallinnas | Tark Kinnisvara",
         "Valminud ja kolimisvalmis korterid Tallinnas ja selle lähiümbruses: hinnad, fotod ja vaatamise broneerimine."),
  'ru': ("Квартиры в продаже в Таллине | Tark Kinnisvara",
         "Готовые квартиры в Таллине и окрестностях: цены, фото и запись на просмотр."),
  'en': ("Flats for sale in Tallinn | Tark Kinnisvara",
         "Finished, move-in-ready flats in Tallinn and nearby: prices, photos and viewing bookings."),
 },
 'kaart': {
  'et': ("Tallinna objektide kaart — müüdud ja müügil | Tark Kinnisvara",
         "Interaktiivne satelliitkaart Tallinna objektidest: üle 200 müüdud ja müügil oleva korteri. Filtreeri staatuse ja aasta järgi."),
  'ru': ("Карта объектов в Таллине — проданные и в продаже | Tark Kinnisvara",
         "Интерактивная спутниковая карта объектов в Таллине: более 200 проданных и продаваемых квартир. Фильтры по статусу и году."),
  'en': ("Map of our Tallinn properties — sold and for sale | Tark Kinnisvara",
         "Interactive satellite map of our Tallinn properties: over 200 sold and for-sale flats. Filter by status and year."),
 },
 'lugu': {
  'et': ("Meie lugu aastate kaupa — Tallinna kaart | Tark Kinnisvara",
         "Vaata, kuidas meie müüdud kodud on aastate jooksul Tallinna kaardile lisandunud: korterite ost, renoveerimine ja müük 2016–2026."),
  'ru': ("Наша история по годам — карта Таллина | Tark Kinnisvara",
         "Смотрите, как проданные нами квартиры год за годом появлялись на карте Таллина: покупка, ремонт и продажа с 2016 по 2026 год."),
  'en': ("Our story year by year — Tallinn map | Tark Kinnisvara",
         "See how the homes we sold appeared on the Tallinn map year after year: buying, renovating and selling from 2016 to 2026."),
 },
 'privacy': {
  'et': ("Privaatsuspoliitika | Tark Kinnisvara", "Kuidas Tark Kinnisvara OÜ töötleb isikuandmeid veebilehel tarkkinnisvara.ee ja kontaktvormi kaudu."),
  'ru': ("Политика конфиденциальности | Tark Kinnisvara", "Как Tark Kinnisvara OÜ обрабатывает персональные данные на сайте tarkkinnisvara.ee и через контактную форму."),
  'en': ("Privacy policy | Tark Kinnisvara", "How Tark Kinnisvara OÜ processes personal data on tarkkinnisvara.ee and through the contact form."),
 },
}
OG_LOCALE = {'et': 'et_EE', 'ru': 'ru_RU', 'en': 'en_GB'}

H1 = {
 'et': "Tark Kinnisvara — korterite ost, renoveerimine ja müük Tallinnas",
 'ru': "Tark Kinnisvara — выкуп, ремонт и продажа квартир в Таллине",
 'en': "Tark Kinnisvara — we buy, renovate and sell flats in Tallinn",
}

# extra TX keys injected into each page's TX dictionary
EXTRA_TX = {
 'index': {
  'et': dict(title=META['index']['et'][0], foot="Pildid: Esri, Maxar · Koordinaadid: Maa- ja Ruumiamet",
             c_p="Jäta oma andmed — vastame esimesel võimalusel. Võid ka helistada.",
             f_consent="Nõustun oma andmete töötlemisega päringule vastamiseks.", f_pp="Privaatsuspoliitika",
             f_fail="Saatmine ebaõnnestus. Palun helista meile:", f_sending="Saadan…", reg="Reg. nr", lg="Privaatsuspoliitika"),
  'ru': dict(title=META['index']['ru'][0], foot="Снимки: Esri, Maxar · Координаты: Maa- ja Ruumiamet",
             c_p="Оставьте данные — ответим при первой возможности. Можно также позвонить.",
             f_consent="Согласен(на) на обработку моих данных для ответа на запрос.", f_pp="Политика конфиденциальности",
             f_fail="Отправить не удалось. Пожалуйста, позвоните нам:", f_sending="Отправляю…", reg="Рег. номер", lg="Политика конфиденциальности"),
  'en': dict(title=META['index']['en'][0], foot="Imagery: Esri, Maxar · Coordinates: Maa- ja Ruumiamet",
             c_p="Leave your details — we'll reply as soon as we can. You can also call us.",
             f_consent="I agree to my data being processed to answer my enquiry.", f_pp="Privacy policy",
             f_fail="Sending failed. Please call us:", f_sending="Sending…", reg="Reg. no.", lg="Privacy policy"),
 },
 'myygil': {
  'et': dict(reg="Reg. nr", pp="Privaatsuspoliitika"),
  'ru': dict(reg="Рег. номер", pp="Политика конфиденциальности"),
  'en': dict(reg="Reg. no.", pp="Privacy policy"),
 },
 'lugu': {
  'et': dict(title=META['lugu']['et'][0], foot="Pildid: Esri, Maxar · Koordinaadid: Maa- ja Ruumiamet", back="← Avalehele"),
  'ru': dict(title=META['lugu']['ru'][0], foot="Снимки: Esri, Maxar · Координаты: Maa- ja Ruumiamet", back="← На главную"),
  'en': dict(title=META['lugu']['en'][0], foot="Imagery: Esri, Maxar · Coordinates: Maa- ja Ruumiamet", back="← Home"),
 },
 'kaart': {
  'et': dict(pp="Privaatsuspoliitika", ly="Aastate kaupa"), 'ru': dict(pp="Политика конфиденциальности", ly="По годам"), 'en': dict(pp="Privacy policy", ly="Year by year"),
 },
}

# ---------------------------------------------------------------- privacy policy
def privacy_html(lang, C, addr_line):
    """Returns (main inner html). Own text for Tark Kinnisvara OÜ."""
    name, reg, tel = C['legalName'], C['regCode'], C['phone']
    AN_TOOLS = 'Google Analytics 4' + (', Meta Pixel' if C.get('fbPixel') else '')
    ctrl_extra = f"<br>{addr_line}" if addr_line else ""
    if lang == 'et':
        return f"""<h1>Privaatsuspoliitika</h1><p class="lead">Kehtib alates 19.11.2026.</p>
<h2>1. Vastutav töötleja</h2><p>{name}, registrikood {reg}{ctrl_extra}<br>Telefon: <a href="tel:{C['phoneE164']}">{tel}</a> · <a href="index.html#kontakt">kontaktvorm</a></p>
<h2>2. Milliseid andmeid me töötleme</h2><p>Kontaktvormi kaudu: nimi, telefon, e-posti aadress, korteri aadress (kui märgid) ja sõnum. Anna meile ainult andmeid, mida soovid meiega jagada. Veebilehe külastamisel võib majutusteenuse pakkuja töödelda sinu IP-aadressi ja brauseri tehnilisi andmeid serveri logides turvalisuse ja töökindluse tagamiseks.</p>
<h2>3. Eesmärk ja õiguslik alus</h2><p>Kasutame andmeid selleks, et vastata sinu päringule, teha korteri hinnang või pakkumine ning leppida kokku vaatamine. Õiguslik alus on sinu nõusolek (isikuandmete kaitse üldmääruse art 6 lg 1 p a) ja lepingu sõlmimiseks tehtavad toimingud sinu taotlusel (art 6 lg 1 p b).</p>
<h2>4. Säilitamine</h2><p>Säilitame päringu andmeid kuni 12 kuud pärast viimast kontakti. Kui sõlmime lepingu, säilitame andmeid seadusest tulenevate tähtaegade jooksul (nt raamatupidamisseadus).</p>
<h2>5. Kellele andmeid edastame</h2><p>Päringud jõuavad meieni e-posti teel (Google, Gmail). Me ei müü ega anna andmeid edasi turundamiseks. Andmeid võime edastada ainult siis, kui see on vajalik sinu päringu täitmiseks (nt notar, pank, hindaja – sinu kokkuleppel) või seadusest tulenevalt. Teenusepakkujad võivad töödelda andmeid väljaspool Euroopa Majanduspiirkonda sobivate kaitsemeetmetega (nt Euroopa Komisjoni tüüptingimused).</p>
<h2>6. Kolmandate osapoolte sisu ja küpsised</h2><p>Statistikat ja küpsiseid ({AN_TOOLS}) kasutame ainult sinu nõusolekul, mille annad lehel kuvatavas teavituses; keeldumisel ei laadita ühtegi jälgimisskripti ega määrata küpsiseid. Statistika abil mõõdame külastusi ja päringuid (telefoni- ja KV.EE-linkide vajutused, vormi saatmine), IP-aadress anonümiseeritakse; seaded saad igal ajal muuta jaluse lingi „Küpsiste seaded“ kaudu. Nõusoleku valik salvestub sinu brauserisse. Kaardi vaatamisel laadib sinu brauser kaardipildid Esri serveritest ning müügil olevate korterite lehel fotod portaalist KV.EE; selle käigus saavad need teenused sinu IP-aadressi. Vaatamise broneerimine ja KV.EE kuulutused avanevad nende pakkujate lehtedel (Calendly, KV.EE), kus kehtivad nende endi privaatsuspoliitikad. Fondid ja skriptid laadime oma serverist.</p>
<h2>7. Sinu õigused</h2><p>Sul on õigus tutvuda oma andmetega, nõuda nende parandamist või kustutamist, piirata töötlemist, esitada vastuväiteid, saada andmed edasikantaval kujul ning võtta nõusolek igal ajal tagasi. Selleks kasuta veebilehe <a href="index.html#kontakt">kontaktvormi</a> või helista numbril <a href="tel:{C['phoneE164']}">{tel}</a>. Kui leiad, et töötleme andmeid valesti, võid pöörduda Andmekaitse Inspektsiooni poole (<a href="https://www.aki.ee" rel="noopener">aki.ee</a>, info@aki.ee).</p>
<h2>8. Muudatused</h2><p>Uuendame seda poliitikat vajaduse korral; kehtiv versioon on alati sellel lehel.</p>"""
    if lang == 'ru':
        return f"""<h1>Политика конфиденциальности</h1><p class="lead">Действует с 19.11.2026.</p>
<h2>1. Ответственный за обработку</h2><p>{name}, регистрационный код {reg}{ctrl_extra}<br>Телефон: <a href="tel:{C['phoneE164']}">{tel}</a> · <a href="index.html#kontakt">контактная форма</a></p>
<h2>2. Какие данные мы обрабатываем</h2><p>Через контактную форму: имя, телефон, адрес e-mail, адрес квартиры (если укажете) и сообщение. Сообщайте только те данные, которыми хотите поделиться. При посещении сайта хостинг-провайдер может обрабатывать ваш IP-адрес и технические данные браузера в журналах сервера для обеспечения безопасности и стабильной работы.</p>
<h2>3. Цель и правовое основание</h2><p>Мы используем данные, чтобы ответить на ваш запрос, оценить квартиру или сделать предложение и согласовать просмотр. Правовое основание: ваше согласие (Общий регламент по защите данных, ст. 6 п. 1 «a») и действия по вашей просьбе до заключения договора (ст. 6 п. 1 «b»).</p>
<h2>4. Срок хранения</h2><p>Данные запроса хранятся до 12 месяцев после последнего контакта. Если мы заключим договор, данные хранятся в течение сроков, установленных законом (например, законом о бухгалтерском учёте).</p>
<h2>5. Кому мы передаём данные</h2><p>Запросы поступают к нам по электронной почте (Google, Gmail). Мы не продаём данные и не передаём их для рекламы. Данные могут передаваться только если это необходимо для выполнения вашего запроса (например, нотариусу, банку, оценщику — по договорённости с вами) или по закону. Поставщики услуг могут обрабатывать данные за пределами Европейской экономической зоны при наличии надлежащих гарантий (например, стандартные договорные условия Европейской комиссии).</p>
<h2>6. Сторонний контент и cookies</h2><p>Статистику и cookies ({AN_TOOLS}) мы используем только с вашего согласия, которое вы даёте в уведомлении на странице; при отказе никакие скрипты отслеживания не загружаются и cookies не устанавливаются. Статистика нужна, чтобы измерять посещения и обращения (клики по телефону и ссылкам KV.EE, отправка формы), IP-адрес анонимизируется; настройки можно изменить в любой момент по ссылке «Настройки cookies» внизу страницы. Выбор сохраняется в вашем браузере. При просмотре карты ваш браузер загружает изображения карты с серверов Esri, а на странице квартир в продаже — фотографии с портала KV.EE; при этом эти сервисы получают ваш IP-адрес. Запись на просмотр и объявления KV.EE открываются на сайтах этих поставщиков (Calendly, KV.EE), где действуют их собственные политики конфиденциальности. Шрифты и скрипты мы загружаем с собственного сервера.</p>
<h2>7. Ваши права</h2><p>Вы вправе получить доступ к своим данным, потребовать их исправления или удаления, ограничить обработку, возразить против неё, получить данные в переносимом формате и в любой момент отозвать согласие. Для этого воспользуйтесь <a href="index.html#kontakt">контактной формой</a> на сайте или позвоните по номеру <a href="tel:{C['phoneE164']}">{tel}</a>. Если вы считаете, что мы обрабатываем данные неправильно, можно обратиться в Инспекцию по защите данных Эстонии (<a href="https://www.aki.ee" rel="noopener">aki.ee</a>, info@aki.ee).</p>
<h2>8. Изменения</h2><p>При необходимости мы обновляем эту политику; действующая версия всегда на этой странице.</p>"""
    return f"""<h1>Privacy policy</h1><p class="lead">Effective from 19 November 2026.</p>
<h2>1. Controller</h2><p>{name}, registry code {reg}{ctrl_extra}<br>Phone: <a href="tel:{C['phoneE164']}">{tel}</a> · <a href="index.html#kontakt">contact form</a></p>
<h2>2. What data we process</h2><p>Through the contact form: name, phone number, e-mail address, flat address (if you provide it) and your message. Please share only what you want us to know. When you visit the site, the hosting provider may process your IP address and browser technical data in server logs to keep the service secure and reliable.</p>
<h2>3. Purpose and legal basis</h2><p>We use the data to answer your enquiry, value your flat or make an offer, and arrange a viewing. The legal basis is your consent (GDPR Art. 6(1)(a)) and steps taken at your request before entering into a contract (Art. 6(1)(b)).</p>
<h2>4. Retention</h2><p>We keep enquiry data for up to 12 months after the last contact. If we enter into a contract, we keep data for the periods required by law (for example, accounting law).</p>
<h2>5. Who receives the data</h2><p>Enquiries reach us by e-mail (Google, Gmail). We do not sell data or pass it on for marketing. We may share data only where needed to fulfil your enquiry (for example a notary, bank or valuer — with your agreement) or where the law requires. Service providers may process data outside the European Economic Area under appropriate safeguards (for example the European Commission's standard contractual clauses).</p>
<h2>6. Third-party content and cookies</h2><p>We use statistics and cookies ({AN_TOOLS}) only with your consent, given in the notice shown on the page; if you decline, no tracking scripts are loaded and no cookies are set. Statistics measure visits and enquiries (clicks on phone and KV.EE links, form submissions); IP addresses are anonymised; you can change your choice at any time via the “Cookie settings” link in the footer. Your choice is stored in your browser. When you view the map, your browser loads map imagery from Esri servers, and on the flats-for-sale page it loads photos from the KV.EE portal; those services receive your IP address. Viewing bookings and KV.EE listings open on those providers' sites (Calendly, KV.EE), which have their own privacy policies. Fonts and scripts are served from our own server.</p>
<h2>7. Your rights</h2><p>You may access your data, ask us to correct or delete it, restrict or object to processing, receive it in a portable format, and withdraw consent at any time. Use the <a href="index.html#kontakt">contact form</a> on this website or call <a href="tel:{C['phoneE164']}">{tel}</a>. If you believe we are processing data unlawfully you can complain to the Estonian Data Protection Inspectorate (<a href="https://www.aki.ee" rel="noopener">aki.ee</a>, info@aki.ee).</p>
<h2>8. Changes</h2><p>We update this policy when needed; the current version is always on this page.</p>"""

PRIVACY_BACK = {'et': "← Avalehele", 'ru': "← На главную", 'en': "← Home"}
NOTFOUND = {'et': ("Lehte ei leitud", "Seda lehte ei ole olemas või see on teisaldatud.", "Avalehele"),
            'ru': ("Страница не найдена", "Такой страницы нет или она перемещена.", "На главную"),
            'en': ("Page not found", "This page does not exist or has moved.", "Back to home")}
NAV_PRIVACY = {'et': "Müügil", 'ru': "В продаже", 'en': "For sale"}

LLMS = """# Tark Kinnisvara

> Tark Kinnisvara OÜ (registry code {reg}) is a Tallinn, Estonia company that buys flats needing renovation and inherited flats, renovates them with its own team, and sells the finished homes. Valuation within 24 hours. Site languages: Estonian, Russian, English.

## What we do
- Buy: flats that need renovation and inherited flats in Tallinn and Harju County; free valuation within 24 hours; fast and safe purchase.
- Renovate: design, construction and finishing by our own team.
- Sell: finished, move-in-ready flats, listed on KV.EE with viewing bookings.

## Key pages
- [Home (Estonian)]({base}/): company overview, services, FAQ, contact form
- [Home (Russian)]({base}/ru/)
- [Home (English)]({base}/en/)
- [Flats for sale]({base}/myygil.html): current listings with prices and photos ([RU]({base}/ru/myygil.html), [EN]({base}/en/myygil.html))
- [Our story year by year]({base}/lugu.html): the same map animated by year
- [Map of properties]({base}/kaart.html): interactive satellite map of sold and for-sale flats in Tallinn
- [Privacy policy]({base}/privacy.html)

## Contact
- Contact form: {base}/#kontakt
- Phone: {tel}
- Company: Tark Kinnisvara OÜ, registry code {reg}, Tallinn, Estonia
"""
