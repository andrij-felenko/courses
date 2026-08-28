const REGISTER: Risk[] = [
  { id: "cloud-brain", what: "Весь розум у хмарі → дім тупіє офлайн",
    probability: "high", impact: "major",
    trigger: "у дизайні правил зʼявився крок, що ходить у хмару на кожну дію",
    owner: "Оля", reviewed: "2026-03-02", state: "open" },        // ← чіпали давно

  { id: "lock-double", what: "Команда замку: дубль або запізнення",
    probability: "med", impact: "major",
    trigger: "у тесті помічено дубль чи запізнення команди",
    owner: "Данило", reviewed: "2026-03-23", state: "open" },

  { id: "firmware-reconnect", what: "Прошивку без джитера не полагодиш",
    probability: "med", impact: "major",
    trigger: "наближається дата заморозки прошивки першої партії",
    owner: "Данило", reviewed: "2026-03-23", state: "open" },

  { id: "vendor-eol", what: "Вендор вимкне хмару → доми-цеглини",
    probability: "low", impact: "catastrophic",
    trigger: "вендора купують / оголосив EOL / близько дата продовження угоди",
    owner: "Оля", reviewed: "2026-03-23", state: "watching" },

  { id: "telemetry-gaps", what: "Дірки в телеметрії офлайн-дому",
    probability: "high", impact: "minor",
    trigger: "частка «дірявих» домів за добу перевалила за фон",
    owner: "Марта", reviewed: "2026-03-23", state: "watching" },

  { id: "room-rename", what: "Два телефони перейменували кімнату",
    probability: "low", impact: "minor",
    trigger: "", owner: "", reviewed: "2026-01-10", state: "accepted" }, // прийнято — не стежимо

  // Щойно на тижні хтось накидав новий страх — і не встиг дописати рядок:
  { id: "ota-unsigned", what: "OTA без підпису → хаб виконає чужу прошивку",
    probability: "unknown", impact: "catastrophic",
    trigger: "", owner: "", reviewed: "2026-03-23", state: "open" },
];
