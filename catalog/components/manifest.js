/* manifest — «Компоненти та розхідники» (тип "catalog"). Схема — AUTHORING.md §2 (v6). Заведено з hardware-інвентарю. */
(window.__BOOKS__ = window.__BOOKS__ || []).push({
  type: "catalog", slug: "components", title: "Компоненти та розхідники",
  sections: [
    { slug: "passives", title: "Пасиви", scope: "Узагальнені пасивні компоненти й дискретні напівпровідники.",
      topics: [
        { slug: "resistor-kit", title: "Набір резисторів", basic: { status: "done" }, detailed: { status: "empty" }, math: [{ file: "math-e-series.md", status: "done" }] },
        { slug: "capacitor-kit", title: "Набір конденсаторів", basic: { status: "done" }, detailed: { status: "empty" }, proj: [{ file: "proj-decode-code.md", status: "done" }] },
        { slug: "transistor-kit", title: "Набір транзисторів (TO-92)", basic: { status: "done" }, detailed: { status: "pending" }, hist: [{ file: "hist-transistor-outline.md", status: "done" }], proj: [{ file: "proj-transistor-switch.md", status: "done" }] },
        { slug: "dip-ics", title: "DIP-мікросхеми (драйвери)", basic: { status: "done" }, detailed: { status: "empty" }, hist: [{ file: "hist-dip-package.md", status: "done" }], proj: [{ file: "proj-driver-basics.md", status: "done" }] },
      ] },
    { slug: "connectors", title: "Зʼєднувачі", scope: "Штирі й сигнальні зʼєднувачі.",
      topics: [
        { slug: "pin-headers", title: "Штирьові зʼєднувачі (male)", basic: { status: "done" }, detailed: { status: "empty" }, hist: [{ file: "hist-dupont-berg.md", status: "done" }] },
        { slug: "jst-gh-cable", title: "JST-GH сигнальний кабель (Pixhawk)", basic: { status: "done" }, detailed: { status: "empty" }, hist: [{ file: "hist-df13-to-gh.md", status: "done" }] },
        { slug: "xt-connectors", title: "Родина силових роз'ємів XT (AMASS: XT30/60/90/120)", basic: { status: "done" }, detailed: { status: "pending" } },
      ] },
    { slug: "cables", title: "Кабелі", scope: "Зʼєднувальні дроти й кабелі.",
      topics: [
        { slug: "dupont-wires", title: "Dupont дроти (M-M/M-F/F-F)", basic: { status: "done" }, detailed: { status: "empty" }, hist: [{ file: "hist-dupont-name.md", status: "done" }], proj: [{ file: "proj-crimp-dupont.md", status: "done" }] },
        { slug: "gpio-ribbon-cable", title: "GPIO шлейф 40-pin", basic: { status: "done" }, detailed: { status: "empty" } },
        { slug: "ethernet-cable", title: "Ethernet-кабель RJ45", basic: { status: "done" }, detailed: { status: "pending" }, hist: [{ file: "hist-two-wiring-standards.md", status: "done" }] },
        { slug: "cable-organizer", title: "Органайзер кабелів (стрічка)", basic: { status: "done" }, detailed: { status: "empty" }, hist: [{ file: "hist-fasteners.md", status: "done" }] },
      ] },
    { slug: "mechanical", title: "Механіка", scope: "Механічні дрібниці.",
      topics: [
        { slug: "servo-horns", title: "Серво-роги (запасні)", basic: { status: "done" }, detailed: { status: "empty" } },
      ] },
    { slug: "consumables", title: "Розхідники", scope: "Витратні матеріали.",
      topics: [
        { slug: "solder-tin", title: "Припій / олово", basic: { status: "done" }, detailed: { status: "pending" }, hist: [{ file: "hist-solder-tin.md", status: "done" }] },
      ] },
  ]
});
