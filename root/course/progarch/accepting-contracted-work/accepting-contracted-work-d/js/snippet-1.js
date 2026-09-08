// .dependency-cruiser.js - декларативна митниця архітектурних меж
module.exports = {
  forbidden: [
    {
      name: "domain-must-not-depend-on-infrastructure",
      comment: "Доменний шар не має права імпортувати адаптери інфраструктури чи ORM",
      severity: "error",
      from: { path: "^src/domain" },
      to: { path: "^src/infrastructure" }
    },
    {
      name: "domain-must-not-depend-on-presentation",
      comment: "Ядро системи ніколи не залежить від HTTP-контролерів чи веб-фреймворків",
      severity: "error",
      from: { path: "^src/domain" },
      to: { path: "^src/api" }
    },
    {
      name: "no-circular-dependencies",
      comment: "Циклічні імпорти між модулями категорично заборонені",
      severity: "error",
      from: {},
      to: { circular: true }
    }
  ]
};
