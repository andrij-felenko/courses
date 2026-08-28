// .dependency-cruiser.cjs — ганяє `depcruise src`; severity:error → білд падає
module.exports = {
  forbidden: [{
    name: "billing-not-into-control",
    comment: "ADR-014: білінг не знає Control. Легальний місток — тільки contracts/.",
    severity: "error",                 // саме error повертає ненульовий код виходу
    from: { path: "^src/billing/" },   // будь-що в білінгу…
    to:   { path: "^src/control/" },   // …не сміє залежати від ядра
  }],
  options: {
    tsPreCompilationDeps: "specify",   // щоб ловити й `import type { Device }` — стерті типи
    doNotFollow: { path: "node_modules" },
  },
};
