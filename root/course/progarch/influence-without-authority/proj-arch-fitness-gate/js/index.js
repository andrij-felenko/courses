// .dependency-cruiser.cjs — одна межа сховища
module.exports = {
  forbidden: [{
    name: "no-db-driver-outside-storage",
    comment: "Драйвер БД — лише в адаптері storage/. Ходи через TelemetryStore. Див. ADR-0007.",
    severity: "warn",                    // спершу warn (не валить білд); згодом — "error"
    from: { pathNot: "^src/storage/" },  // будь-що поза адаптером…
    to:   { path: "^node_modules/pg/" }, // …не сміє тягнути драйвер
  }],
};
