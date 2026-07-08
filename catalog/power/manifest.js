/* manifest — «Живлення» (тип "catalog"). Схема — AUTHORING.md §2 (v6). Заведено з hardware-інвентарю. */
(window.__BOOKS__ = window.__BOOKS__ || []).push({
  type: "catalog", slug: "power", title: "Живлення",
  sections: [
    { slug: "batteries", title: "Акумулятори й HAT", scope: "Елементи живлення й плати-живильники.",
      topics: [
        { slug: "liion-hat-rpi", title: "Li-ion Battery HAT для Raspberry Pi", basic: { status: "done" }, detailed: { status: "empty" }, proj: [ { file: "proj-read-battery.md", status: "done" } ] },
        { slug: "videx-14500", title: "Videx 14500 — Li-ion 3.7V", basic: { status: "done" }, detailed: { status: "empty" }, hist: [ { file: "hist-lithium-ion.md", status: "done" } ] },
        { slug: "lipo-3s", title: "LiPo-акумулятор (XT60, ~3S)", basic: { status: "done" }, detailed: { status: "pending" }, hist: [ { file: "hist-lipo-birth.md", status: "done" } ], math: [ { file: "math-c-rate.md", status: "done" } ] },
        { slug: "power-hat-family", title: "Родина живильних HAT-ів Waveshare (SW6106)", basic: { status: "done" }, detailed: { status: "pending" }, proj: [ { file: "proj-i2c-fuel.md", status: "done" } ] },
      ] },
    { slug: "regulators", title: "Перетворювачі", scope: "DC-DC перетворювачі й модулі живлення.",
      topics: [
        { slug: "yp-08-power", title: "YP-08 — модуль живлення", basic: { status: "done" }, detailed: { status: "empty" }, proj: [ { file: "proj-rail-monitor.md", status: "done" } ] },
        { slug: "dcdc-buck-boost", title: "Програмований DC-DC buck-boost (DPS/DPH)", basic: { status: "done" }, detailed: { status: "pending" }, hist: [ { file: "hist-ruideng-opendps.md", status: "done" } ], proj: [ { file: "proj-modbus-control.md", status: "done" } ] },
        { slug: "xc6206", title: "XC6206 (662K) — LDO-регулятор 3.3 В", basic: { status: "done" }, detailed: { status: "empty" }, hist: [ { file: "hist-torex-ldo.md", status: "done" } ] },
        { slug: "bec-ubec", title: "BEC / UBEC — понижувальне живлення для серв і приймача", basic: { status: "done" }, detailed: { status: "pending" }, hist: [ { file: "hist-battery-eliminator.md", status: "done" } ], proj: [ { file: "proj-servo-rail.md", status: "done" } ] },
      ] },
    { slug: "drivers-relays", title: "Драйвери й реле", scope: "Ключі навантаження: реле, драйвери моторів/крокових.",
      topics: [
        { slug: "relay-5v", title: "5V реле-модуль (Songle SRD-05VDC)", basic: { status: "done" }, detailed: { status: "pending" }, proj: [ { file: "proj-relay-control.md", status: "done" } ] },
        { slug: "mc33886-driver", title: "CJMCU MC33886 — драйвер моторів (5A H-міст)", basic: { status: "done" }, detailed: { status: "pending" }, hist: [ { file: "hist-smartmos.md", status: "done" } ], proj: [ { file: "proj-motor-control.md", status: "done" } ] },
        { slug: "uln2003-driver", title: "ULN2003 — драйвер (плата для 28BYJ-48)", basic: { status: "done" }, detailed: { status: "pending" }, hist: [ { file: "hist-uln-sprague.md", status: "done" } ], proj: [ { file: "proj-uln2003-api.md", status: "done" } ] },
      ] },
  ]
});
