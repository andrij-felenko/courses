// .dependency-cruiser.cjs (TypeScript) — dependency-cruiser: forbidden + no-circular
module.exports = {
  forbidden: [
    { name: "billing-not-control", severity: "error",
      comment: "білінг не сміє знати control — лише подія",
      from: { path: "^src/billing" }, to: { path: "^src/control" } },
    { name: "no-circular", severity: "error",
      comment: "жодних циклів у графі модулів",
      from: {}, to: { circular: true } },              // ← ациклічність однією умовою
    { name: "cross-module-only-via-index", severity: "error",
      comment: "у чужий модуль — лише через його index-бар'єр, не в нутрощі",
      from: { path: "^src/([^/]+)/" },              // $1 = модуль-власник файлу
      to:   { path: "^src/[^/]+/[^/]+",             // глибокий шлях у якийсь модуль…
              pathNot: ["^src/[^/]+/index\\.ts$",   // …дозволено лише через index…
                        "^src/$1/"] } },            // …або якщо це той самий модуль ($1)
  ],
};
