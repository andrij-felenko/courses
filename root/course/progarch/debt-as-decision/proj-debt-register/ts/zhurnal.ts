const JOURNAL: Debt[] = [
  { id: "DH-014",
    body: "kwhForDay сканує всю сиру телеметрію оселі на кожен запит",
    why: "панель — платна фіча з дедлайном; rollup — 2 тижні, наївно — 2 дні",
    seam: "EnergyRollup", interest: "час відповіді росте лінійно з пристроями оселі",
    trigger: [{ metric: "panel_p95_ms", op: ">", threshold: 800 },
              { metric: "max_devices_per_home", op: ">", threshold: 5000 }],
    repay: "BucketedRollup на композиційному корені",
    test: "характеризаційний тест пінить числа NaiveRollup",
    owner: "команда Telemetry", state: "open" },

  { id: "DH-031",
    body: "нічний експорт CSV збирає весь місяць у пам'ять",
    why: "перший корпоративний клієнт просив «вже»; стрімінг — потім",
    seam: "MonthlyExport", interest: "пік пам'яті росте з розміром оселі",
    trigger: [{ metric: "export_lag_s", op: ">", threshold: 120 }],  // ← метрики ще нема у знімку
    repay: "потоковий експорт партіями", test: "золотий CSV на еталонній оселі",
    owner: "команда Data", state: "open" },

  { id: "DH-019",
    body: "правила автоматизації тримаються в одному JSON-полі",
    why: "форму правил ще шукали — не хотіли фіксувати схему рано",
    seam: "RuleStore", interest: "кожен новий тип правила чіпає парсинг усього поля",
    trigger: [{ metric: "rule_types", op: ">", threshold: 6 }],
    repay: "нормалізована таблиця правил", test: "снапшот чинних правил",
    owner: "", state: "open" },   // ← власника не призначили, і маркера в коді вже нема

  { id: "DH-007",
    body: "перша версія парсера телеметрії на регулярках",
    why: "треба було завести хоч якісь дані з першого хабу",
    seam: "TelemetryParser", interest: "—",
    trigger: [], repay: "бінарний декодер за схемою (зроблено)",
    test: "корпус реальних кадрів", owner: "Данило", state: "closed" }, // ← погашено, та маркер завис
];
