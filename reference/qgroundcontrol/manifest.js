/* reference/qgroundcontrol/manifest.js — ДОВІДНИК «QGroundControl» (тип "reference").
   Довідник — 4-й вид книги (AUTHORING §1): конкретна рукотворна система з версіями,
   релізами й власною архітектурою. Питання «а в якій версії?» тут доречне завжди.

   МЕЖА (§1). Сам протокол MAVLink, місії, параметри й телеметрія як ПРОТОКОЛИ живуть у
   book/communications/protocols; автопілоти — у book/programming/embedded-systems;
   порівняння GCS уже написане власною статтею guide/embedded. Сюди йде ЛИШЕ те, що є
   влаштуванням саме цього застосунку: його підсистеми, точки розширення, збірка.

   ⚠️ Qt/QML як тема сюди НЕ входить і не входитиме (свідоме рішення): описуємо підсистеми
   QGC (Vehicle, FactSystem, LinkManager, план, карта, відео), а не фреймворк, на якому вони стоять.

   30 тем у 6 розділах. Усі заведено як detailed:pending (basic — за потреби, §3). */
(window.__BOOKS__ = window.__BOOKS__ || []).push({
  type: "reference", slug: "qgroundcontrol", title: "QGroundControl",
  sections: [
    { slug: "overview", title: "Що це і як влаштований проєкт", scope: "Призначення застосунку, його користувачі, модель релізів і вендорські збірки.",
      topics: [
        { slug: "what-is-qgc", title: "QGroundControl: що це і яку задачу розв'язує", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "user-roles", title: "Три користувачі станції: пілот, налаштувальник, розробник", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "project-and-forks", title: "Проєкт, ліцензія й вендорські форки", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "release-model", title: "Модель релізів: стабільні, денні збірки, версії", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "architecture", title: "Архітектура застосунку", scope: "Головні підсистеми й те, як стан апарата доходить від байтів до екрана.",
      topics: [
        { slug: "app-composition", title: "З чого складається застосунок: шари й запуск", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "core-plugin", title: "Ядрове розширення: головна точка кастомізації", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "vehicle-object", title: "Vehicle: модель апарата всередині застосунку", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "fact-system", title: "FactSystem: факт, метадані й зв'язок зі станом", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "parameter-manager", title: "Менеджер параметрів: завантаження, кеш, запис", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "multi-vehicle", title: "Кілька апаратів в одному застосунку", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "settings-persistence", title: "Налаштування й що переживає перезапуск", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "threading-model", title: "Модель потоків: де живуть лінк, розбір і відмальовка", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "links", title: "Канали й протокол", scope: "Як застосунок під'єднується до апарата і що робить із потоком повідомлень.",
      topics: [
        { slug: "link-manager", title: "Менеджер каналів: облік і життєвий цикл з'єднань", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "link-types", title: "Типи каналів: серійний, UDP, TCP, Bluetooth", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "mavlink-handling", title: "Обробка MAVLink: розбір, версії, канали", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "message-routing", title: "Маршрутизація за sysid і compid", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "telemetry-logging", title: "Запис телеметрії й відтворення логів", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "planning", title: "Планування місій", scope: "Модель плану в застосунку: з чого він складається і як потрапляє на борт.",
      topics: [
        { slug: "plan-model", title: "Модель плану: місія, геозона, точки збору", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "mission-items", title: "Елементи місії й команди", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "survey-patterns", title: "Патерни зйомки: полігон, коридор, структура", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "terrain-and-altitude", title: "Рельєф і режими висоти в плані", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "plan-exchange", title: "Обмін планом із апаратом: вивантаження й звірка", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "map-video", title: "Карта й відео", scope: "Дві найважчі підсистеми станції: тайлова карта й відеотракт.",
      topics: [
        { slug: "map-engine", title: "Рушій карти: провайдери, тайли, рівні масштабу", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "offline-maps", title: "Офлайн-карти й кеш тайлів", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "video-manager", title: "Відеопідсистема: джерела, керування, запис", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "video-pipeline", title: "Відеотракт станції на GStreamer", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "build-extend", title: "Збірка й розширення", scope: "Як зібрати застосунок під три платформи й як додати до нього своє.",
      topics: [
        { slug: "building-qgc", title: "Збірка QGroundControl: залежності й кроки", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "platform-targets", title: "Цілі платформ: Linux, Windows, Android", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "custom-build", title: "Власна збірка: набір функцій і бренд", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "custom-mavlink-messages", title: "Власні MAVLink-повідомлення в застосунку", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "contributing", title: "Внесок в апстрим: процес, вимоги, рев'ю", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
  ]
});
