/* manifest — «Живлення» (тип "catalog"). Схема — AUTHORING.md §2 (v6). Заведено з hardware-інвентарю. */
(window.__BOOKS__ = window.__BOOKS__ || []).push({
  type: "catalog", slug: "power", title: "Живлення",
  sections: [
    { slug: "batteries", title: "Акумулятори й HAT", scope: "Елементи живлення й плати-живильники.",
      topics: [
        { slug: "liion-hat-rpi", title: "Li-ion Battery HAT для Raspberry Pi", basic: { status: "pending" }, detailed: { status: "empty" } },
        { slug: "videx-14500", title: "Videx 14500 — Li-ion 3.7V", basic: { status: "pending" }, detailed: { status: "empty" } },
        { slug: "lipo-3s", title: "LiPo-акумулятор (XT60, ~3S)", basic: { status: "pending" }, detailed: { status: "empty" } },
      ] },
    { slug: "regulators", title: "Перетворювачі", scope: "DC-DC перетворювачі й модулі живлення.",
      topics: [
        { slug: "yp-08-power", title: "YP-08 — модуль живлення", basic: { status: "pending" }, detailed: { status: "empty" } },
        { slug: "dcdc-buck-boost", title: "Програмований DC-DC buck-boost (DPS/DPH)", basic: { status: "pending" }, detailed: { status: "empty" } },
      ] },
    { slug: "drivers-relays", title: "Драйвери й реле", scope: "Ключі навантаження: реле, драйвери моторів/крокових.",
      topics: [
        { slug: "relay-5v", title: "5V реле-модуль (Songle SRD-05VDC)", basic: { status: "pending" }, detailed: { status: "empty" } },
        { slug: "mc33886-driver", title: "CJMCU MC33886 — драйвер моторів (5A H-міст)", basic: { status: "pending" }, detailed: { status: "empty" } },
        { slug: "uln2003-driver", title: "ULN2003 — драйвер (плата для 28BYJ-48)", basic: { status: "pending" }, detailed: { status: "empty" } },
      ] },
  ]
});
