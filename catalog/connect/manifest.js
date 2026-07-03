/* manifest — «Звʼязок» (тип "catalog"). Схема — AUTHORING.md §2 (v6). Заведено з hardware-інвентарю. */
(window.__BOOKS__ = window.__BOOKS__ || []).push({
  type: "catalog", slug: "connect", title: "Звʼязок",
  sections: [
    { slug: "radio", title: "Радіомодулі", scope: "Готові модулі радіозвʼязку й передавання даних.",
      topics: [
        { slug: "nrf24-radio", title: "Радіомодуль nRF24", basic: { status: "pending" }, detailed: { status: "empty" } },
        { slug: "lora-module", title: "LoRa-модуль", basic: { status: "done" }, detailed: { status: "pending" } },
        { slug: "fpv-telemetry-air", title: "FPV-телеметрія — повітряний модуль", basic: { status: "pending" }, detailed: { status: "empty" } },
        { slug: "fpv-telemetry-ground", title: "FPV-телеметрія — наземний модуль", basic: { status: "pending" }, detailed: { status: "empty" } },
        { slug: "bluetooth-hc05", title: "Bluetooth-модуль HC-05/HC-06", basic: { status: "pending" }, detailed: { status: "empty" } },
      ] },
    { slug: "gnss", title: "Супутникова навігація", scope: "GNSS/GPS-приймачі.",
      topics: [
        { slug: "beitian-be182", title: "Beitian BE-182 — GNSS/GPS-модуль", basic: { status: "pending" }, detailed: { status: "empty" } },
      ] },
    { slug: "rfid", title: "RFID", scope: "Зчитувачі й мітки радіочастотної ідентифікації.",
      topics: [
        { slug: "rfid-rc522", title: "RFID-RC522 — зчитувач 13.56 МГц", basic: { status: "pending" }, detailed: { status: "empty" } },
        { slug: "rfid-tag", title: "RFID-брелок (13.56 МГц)", basic: { status: "pending" }, detailed: { status: "empty" } },
      ] },
    { slug: "ir", title: "Інфрачервоний звʼязок", scope: "ІЧ передавачі й приймачі (пульти).",
      topics: [
        { slug: "ky-005-ir-tx", title: "KY-005 — ІЧ-передавач", basic: { status: "pending" }, detailed: { status: "empty" } },
        { slug: "ky-022-ir-rx", title: "KY-022 — ІЧ-приймач (на платі)", basic: { status: "pending" }, detailed: { status: "empty" } },
        { slug: "vs1838b-ir-rx", title: "VS1838B — ІЧ-приймач", basic: { status: "pending" }, detailed: { status: "empty" } },
      ] },
  ]
});
