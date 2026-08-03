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
        { slug: "what-is-qgc", title: "QGroundControl: що це і яку задачу розв'язує", basic: { status: "empty" }, detailed: { status: "done" } , hist: [{ file: "hist-qgc-birth.md", status: "done" }] , proj: [{ file: "proj-minimal-gcs.md", status: "done" }] },
        { slug: "user-roles", title: "Три користувачі станції: пілот, налаштувальник, розробник", basic: { status: "empty" }, detailed: { status: "done" } , api: [{ file: "api-visibility-knobs.md", status: "done" }] , proj: [{ file: "proj-role-gated-control.md", status: "done" }] },
        { slug: "project-and-forks", title: "Проєкт, ліцензія й вендорські форки", basic: { status: "empty" }, detailed: { status: "done" } , hist: [{ file: "hist-qgc-origins.md", status: "done" }] , proj: [{ file: "proj-fork-divergence.md", status: "done" }] },
        { slug: "release-model", title: "Модель релізів: стабільні, денні збірки, версії", basic: { status: "empty" }, detailed: { status: "done" } , hist: [{ file: "hist-version-lines.md", status: "done" }] , proj: [{ file: "proj-version-from-git.md", status: "done" }] },
      ] },

    { slug: "architecture", title: "Архітектура застосунку", scope: "Головні підсистеми й те, як стан апарата доходить від байтів до екрана.",
      topics: [
        { slug: "app-composition", title: "З чого складається застосунок: шари й запуск", basic: { status: "empty" }, detailed: { status: "done" } , hist: [{ file: "hist-toolbox.md", status: "done" }] , proj: [{ file: "proj-byte-to-fact.md", status: "done" }] },
        { slug: "core-plugin", title: "Ядрове розширення: головна точка кастомізації", basic: { status: "empty" }, detailed: { status: "done" } , api: [{ file: "api-core-plugin.md", status: "done" }] , proj: [{ file: "proj-custom-plugin.md", status: "done" }] },
        { slug: "vehicle-object", title: "Vehicle: модель апарата всередині застосунку", basic: { status: "empty" }, detailed: { status: "done" } , api: [{ file: "api-vehicle-qml.md", status: "done" }] , proj: [{ file: "proj-message-to-property.md", status: "done" }] },
        { slug: "fact-system", title: "FactSystem: факт, метадані й зв'язок зі станом", basic: { status: "empty" }, detailed: { status: "done" } , api: [{ file: "api-fact.md", status: "done" }] , proj: [{ file: "proj-custom-factgroup.md", status: "done" }] },
        { slug: "parameter-manager", title: "Менеджер параметрів: завантаження, кеш, запис", basic: { status: "done" }, detailed: { status: "done" } , proj: [{ file: "proj-param-sync.md", status: "done" }, { file: "proj-param-pck.md", status: "done" }] , api: [{ file: "api-param-manager.md", status: "done" }] },
        { slug: "multi-vehicle", title: "Кілька апаратів в одному застосунку", basic: { status: "empty" }, detailed: { status: "done" } , proj: [{ file: "proj-vehicle-lookup.md", status: "done" }] , api: [{ file: "api-multivehiclemanager.md", status: "done" }] },
        { slug: "settings-persistence", title: "Налаштування й що переживає перезапуск", basic: { status: "done" }, detailed: { status: "done" } , api: [{ file: "api-settings-file.md", status: "done" }] , proj: [{ file: "proj-settings-group.md", status: "done" }] },
        { slug: "threading-model", title: "Модель потоків: де живуть лінк, розбір і відмальовка", basic: { status: "empty" }, detailed: { status: "done" } , api: [{ file: "api-thread-crossing.md", status: "done" }] , proj: [{ file: "proj-link-worker.md", status: "done" }] },
        { slug: "firmware-plugin", title: "Плагін прошивки: як станція ховає різницю між автопілотами", basic: { status: "done" }, detailed: { status: "done" } , api: [{ file: "api-firmware-plugin.md", status: "done" }] , proj: [{ file: "proj-custom-firmware-plugin.md", status: "done" }] },
        { slug: "component-information", title: "Відомості про компонент: метадані з борту", basic: { status: "empty" }, detailed: { status: "done" } , api: [{ file: "api-component-metadata.md", status: "done" }] , proj: [{ file: "proj-metadata-client.md", status: "done" }] },
        { slug: "events-interface", title: "Інтерфейс подій: коди з борту як людські повідомлення", basic: { status: "empty" }, detailed: { status: "done" } , hist: [{ file: "hist-statustext-to-events.md", status: "done" }] , api: [{ file: "api-events-messages.md", status: "done" }] , proj: [{ file: "proj-event-receiver.md", status: "done" }] },
        { slug: "actuator-config", title: "Налаштування виконавчих механізмів: геометрія, виходи, перевірка", basic: { status: "empty" }, detailed: { status: "done" } , api: [{ file: "api-actuator-metadata.md", status: "done" }] , proj: [{ file: "proj-actuator-test-client.md", status: "done" }] , hist: [{ file: "hist-mixer-files.md", status: "done" }] },
      ] },

    { slug: "links", title: "Канали й протокол", scope: "Як застосунок під'єднується до апарата і що робить із потоком повідомлень.",
      topics: [
        { slug: "link-manager", title: "Менеджер каналів: облік і життєвий цикл з'єднань", basic: { status: "empty" }, detailed: { status: "done" } , proj: [{ file: "proj-channel-allocator.md", status: "done" }] , api: [{ file: "api-linkmanager.md", status: "done" }] },
        { slug: "link-types", title: "Типи каналів: серійний, UDP, TCP, Bluetooth", basic: { status: "done" }, detailed: { status: "done" } , api: [{ file: "api-link-config.md", status: "done" }] , proj: [{ file: "proj-udp-endpoint.md", status: "done" }] , comp: [{ file: "comp-serial-adapters.md", status: "done" }] },
        { slug: "mavlink-handling", title: "Обробка MAVLink: розбір, версії, канали", basic: { status: "empty" }, detailed: { status: "done" } , proj: [{ file: "proj-parse-channel.md", status: "done" }] , math: [{ file: "math-loss-counting.md", status: "done" }] },
        { slug: "message-routing", title: "Маршрутизація за sysid і compid", basic: { status: "empty" }, detailed: { status: "done" } , proj: [{ file: "proj-router-dispatch.md", status: "done" }] , api: [{ file: "api-mavlink-ids.md", status: "done" }] },
        { slug: "telemetry-logging", title: "Запис телеметрії й відтворення логів", basic: { status: "done" }, detailed: { status: "done" } , api: [{ file: "api-tlog-format.md", status: "done" }] , proj: [{ file: "proj-tlog-reader.md", status: "done" }] },
        { slug: "mavlink-inspector", title: "Інспектор MAVLink: перегляд сирого трафіку", basic: { status: "empty" }, detailed: { status: "done" } , proj: [{ file: "proj-inspector-tap.md", status: "done" }] , math: [{ file: "math-rate-estimator.md", status: "done" }] , api: [{ file: "api-inspector-qml.md", status: "done" }] },
        { slug: "vehicle-logs", title: "Бортові логи апарата: завантаження й потокове передавання", basic: { status: "empty" }, detailed: { status: "done" } , api: [{ file: "api-log-protocol.md", status: "done" }] , proj: [{ file: "proj-log-downloader.md", status: "done" }] , hist: [{ file: "hist-log-protocol-origins.md", status: "done" }] },
        { slug: "log-viewer", title: "Переглядач логів: графіки й повідомлення з бортового файлу", basic: { status: "empty" }, detailed: { status: "done" } , api: [{ file: "api-log-formats.md", status: "done" }] , proj: [{ file: "proj-dataflash-reader.md", status: "done" }] , hist: [{ file: "hist-log-analysis-outside.md", status: "done" }] },
      ] },

    { slug: "planning", title: "Планування місій", scope: "Модель плану в застосунку: з чого він складається і як потрапляє на борт.",
      topics: [
        { slug: "plan-model", title: "Модель плану: місія, геозона, точки збору", basic: { status: "done" }, detailed: { status: "done" } , api: [{ file: "api-plan-file.md", status: "done" }] , proj: [{ file: "proj-plan-json-roundtrip.md", status: "done" }] },
        { slug: "mission-items", title: "Елементи місії й команди", basic: { status: "empty" }, detailed: { status: "done" } , api: [{ file: "api-mission-command-json.md", status: "done" }] , proj: [{ file: "proj-plan-to-items.md", status: "done" }] , math: [{ file: "math-coordinate-precision.md", status: "done" }] },
        { slug: "survey-patterns", title: "Патерни зйомки: полігон, коридор, структура", basic: { status: "empty" }, detailed: { status: "done" } , math: [{ file: "math-footprint-arithmetic.md", status: "done" }] , proj: [{ file: "proj-transect-generator.md", status: "done" }] , api: [{ file: "api-transect-commands.md", status: "done" }] },
        { slug: "terrain-and-altitude", title: "Рельєф і режими висоти в плані", basic: { status: "empty" }, detailed: { status: "done" } , proj: [{ file: "proj-terrain-follow-path.md", status: "done" }] , api: [{ file: "api-terrain-query.md", status: "done" }] },
        { slug: "plan-exchange", title: "Обмін планом із апаратом: вивантаження й звірка", basic: { status: "done" }, detailed: { status: "done" } , api: [{ file: "api-mission-protocol.md", status: "done" }] , proj: [{ file: "proj-plan-upload.md", status: "done" }] , hist: [{ file: "hist-mission-protocol-evolution.md", status: "done" }] },
      ] },

    { slug: "map-video", title: "Карта й відео", scope: "Дві найважчі підсистеми станції: тайлова карта й відеотракт.",
      topics: [
        { slug: "map-engine", title: "Рушій карти: провайдери, тайли, рівні масштабу", basic: { status: "empty" }, detailed: { status: "done" } , proj: [{ file: "proj-custom-map-source.md", status: "done" }] , api: [{ file: "api-map-provider.md", status: "done" }] },
        { slug: "offline-maps", title: "Офлайн-карти й кеш тайлів", basic: { status: "empty" }, detailed: { status: "done" } , proj: [{ file: "proj-seed-cache.md", status: "done" }] , api: [{ file: "api-tile-cache-db.md", status: "done" }] },
        { slug: "video-manager", title: "Відеопідсистема: джерела, керування, запис", basic: { status: "done" }, detailed: { status: "done" } , proj: [{ file: "proj-telemetry-subtitles.md", status: "done" }, { file: "proj-source-resolution.md", status: "done" }] , api: [{ file: "api-videomanager.md", status: "done" }] },
        { slug: "video-pipeline", title: "Відеотракт станції на GStreamer", basic: { status: "done" }, detailed: { status: "done" } , proj: [{ file: "proj-min-video-pipeline.md", status: "done" }] , api: [{ file: "api-gst-receiver.md", status: "done" }] , hist: [{ file: "hist-video-sink.md", status: "done" }] },
      ] },

    { slug: "build-extend", title: "Збірка й розширення", scope: "Як зібрати застосунок під три платформи й як додати до нього своє.",
      topics: [
        { slug: "building-qgc", title: "Збірка QGroundControl: залежності й кроки", basic: { status: "done" }, detailed: { status: "done" } , proj: [{ file: "proj-mavlink-codegen.md", status: "done" }] , hist: [{ file: "hist-qmake-to-cmake.md", status: "done" }] , api: [{ file: "api-build-options.md", status: "done" }] },
        { slug: "platform-targets", title: "Цілі платформ: Linux, Windows, Android", basic: { status: "done" }, detailed: { status: "done" } , proj: [{ file: "proj-android-serial-bridge.md", status: "done" }] , api: [{ file: "api-platform-knobs.md", status: "done" }] },
        { slug: "custom-build", title: "Власна збірка: набір функцій і бренд", basic: { status: "empty" }, detailed: { status: "done" } , api: [{ file: "api-custom-overrides.md", status: "done" }] , proj: [{ file: "proj-custom-overlay-repo.md", status: "done" }] },
        { slug: "custom-mavlink-messages", title: "Власні MAVLink-повідомлення в застосунку", basic: { status: "empty" }, detailed: { status: "done" } , api: [{ file: "api-dialect-xml.md", status: "done" }] , math: [{ file: "math-crc-extra.md", status: "done" }] , proj: [{ file: "proj-custom-message.md", status: "done" }] },
        { slug: "contributing", title: "Внесок в апстрим: процес, вимоги, рев'ю", basic: { status: "empty" }, detailed: { status: "done" } , api: [{ file: "api-contrib-gates.md", status: "done" }] , proj: [{ file: "proj-local-gate.md", status: "done" }] },
      ] },
  ]
});
