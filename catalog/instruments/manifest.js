/* manifest — «Прилади й приладдя» (тип "catalog"). Схема — AUTHORING.md §2 (v6). Заведено з hardware-інвентарю. */
(window.__BOOKS__ = window.__BOOKS__ || []).push({
  type: "catalog", slug: "instruments", title: "Прилади й приладдя",
  sections: [
    { slug: "prototyping", title: "Прототипування", scope: "Макетні плати й ручний інструмент.",
      topics: [
        { slug: "breadboard-large", title: "Макетна плата (велика)", basic: { status: "empty" }, detailed: { status: "done" }, hist: [{ file: "hist-breadboard-name.md", status: "done" }], proj: [{ file: "proj-blink-wiring.md", status: "done" }] },
        { slug: "breadboard-mini", title: "Макетна плата (міні)", basic: { status: "empty" }, detailed: { status: "done" }, hist: [{ file: "hist-solderless-breadboard.md", status: "done" }] },
        { slug: "side-cutters", title: "Бокорізи", basic: { status: "empty" }, detailed: { status: "done" }, hist: [{ file: "hist-birth-of-cutters.md", status: "done" }] },
        { slug: "crimp-tool", title: "Обтискні кліщі (Dupont/JST)", basic: { status: "empty" }, detailed: { status: "done" }, hist: [{ file: "hist-crimp-invention.md", status: "done" }] },
      ] },
    { slug: "fabrication", title: "Виготовлення", scope: "Виробниче обладнання.",
      topics: [
        { slug: "3d-printer", title: "3D-принтер", basic: { status: "empty" }, detailed: { status: "done" }, hist: [{ file: "hist-reprap.md", status: "done" }], proj: [{ file: "proj-gcode.md", status: "done" }], api: [{ file: "api-gcode.md", status: "done" }] },
      ] },
  ]
});
