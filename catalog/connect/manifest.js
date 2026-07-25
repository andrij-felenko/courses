/* manifest — «Звʼязок» (тип "catalog"). Схема — AUTHORING.md §2 (v6). Заведено з hardware-інвентарю. */
(window.__BOOKS__ = window.__BOOKS__ || []).push({
  type: "catalog", slug: "connect", title: "Звʼязок",
  sections: [
    { slug: "radio", title: "Радіомодулі", scope: "Готові модулі радіозвʼязку й передавання даних.",
      topics: [
        { slug: "nrf24-radio", title: "Радіомодуль nRF24", basic: { status: "empty" }, detailed: { status: "done" }, api: [{ file: "api-nrf24.md", status: "done" }, { file: "api-esb.md", status: "done" }] },
        { slug: "lora-module", title: "LoRa-модуль", basic: { status: "empty" }, detailed: { status: "done" } },
        { slug: "fpv-telemetry-air", title: "FPV-телеметрія — повітряний модуль", basic: { status: "empty" }, detailed: { status: "done" }, hist: [{ file: "hist-sik-birth.md", status: "done" }], api: [{ file: "api-sik-config.md", status: "done" }] },
        { slug: "fpv-telemetry-ground", title: "FPV-телеметрія — наземний модуль", basic: { status: "empty" }, detailed: { status: "done" }, hist: [{ file: "hist-sik-radio.md", status: "done" }], proj: [{ file: "proj-read-telemetry.md", status: "done" }], api: [{ file: "api-serial-mavlink.md", status: "done" }] },
        { slug: "bluetooth-hc05", title: "Bluetooth-модуль HC-05/HC-06", basic: { status: "empty" }, detailed: { status: "done" }, hist: [{ file: "hist-hc-series.md", status: "done" }], proj: [{ file: "proj-hc05-car.md", status: "done" }], api: [{ file: "api-hc05-uart.md", status: "done" }] },
        { slug: "elrs-air-unit", title: "Повітряний блок ExpressLRS/mLRS (телеметрія + керування)", basic: { status: "empty" }, detailed: { status: "done" }, api: [{ file: "api-elrs-config.md", status: "done" }] },
      ] },
    { slug: "gnss", title: "Супутникова навігація", scope: "GNSS/GPS-приймачі.",
      topics: [
        { slug: "beitian-be182", title: "Beitian BE-182 — GNSS/GPS-модуль", basic: { status: "empty" }, detailed: { status: "done" }, hist: [{ file: "hist-ublox-m10.md", status: "done" }], proj: [{ file: "proj-nmea-read.md", status: "done" }], api: [{ file: "api-nmea-ubx.md", status: "done" }] },
      ] },
    { slug: "rfid", title: "RFID", scope: "Зчитувачі й мітки радіочастотної ідентифікації.",
      topics: [
        { slug: "rfid-rc522", title: "RFID-RC522 — зчитувач 13.56 МГц", basic: { status: "empty" }, detailed: { status: "done" }, hist: [{ file: "hist-mifare-crypto1.md", status: "done" }], api: [{ file: "api-rc522.md", status: "done" }] },
        { slug: "rfid-tag", title: "RFID-брелок (13.56 МГц)", basic: { status: "empty" }, detailed: { status: "done" }, hist: [{ file: "hist-mifare-crypto1.md", status: "done" }], math: [{ file: "math-coupling.md", status: "done" }], api: [{ file: "api-read-write.md", status: "done" }] },
      ] },
    { slug: "ir", title: "Інфрачервоний звʼязок", scope: "ІЧ передавачі й приймачі (пульти).",
      topics: [
        { slug: "ky-005-ir-tx", title: "KY-005 — ІЧ-передавач", basic: { status: "empty" }, detailed: { status: "done" }, proj: [{ file: "proj-clone-remote.md", status: "done" }], api: [{ file: "api-irremote-nec.md", status: "done" }] },
        { slug: "ky-022-ir-rx", title: "KY-022 — ІЧ-приймач (на платі)", basic: { status: "empty" }, detailed: { status: "done" }, proj: [{ file: "proj-irremote-menu.md", status: "done" }], api: [{ file: "api-irremote-decode.md", status: "done" }] },
        { slug: "vs1838b-ir-rx", title: "VS1838B — ІЧ-приймач", basic: { status: "empty" }, detailed: { status: "done" }, api: [{ file: "api-nec-decode.md", status: "done" }] },
        { slug: "ky-series", title: "Родина KY-xxx (Keyes «37 в одному»)", basic: { status: "empty" }, detailed: { status: "done" }, hist: [{ file: "hist-ir-remote.md", status: "done" }] },
      ] },
  ]
});
