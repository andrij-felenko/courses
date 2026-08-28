type Status = "open" | "armed" | "due" | "superseded";
type Dir = "rising" | "falling";        // куди «погано»: метрика росте чи падає

interface Condition {
  signal: string;   // ключ метрики у знімку, напр. "search.p99_ms"
  dir: Dir;
  armAt: number;    // поріг зведення — увійти в смугу спостереження
  fireAt: number;   // поріг спрацювання (для rising: armAt ≤ fireAt)
}

interface Trigger {
  conditions: Condition[];   // може стежити за кількома сигналами
  mode: "all" | "any";       // поєднати їх кон'юнкцією чи диз'юнкцією
  holdFor: number;           // скільки вимірів поспіль умова має триматися
  leadWeeks: number;         // L — на скільки наперед прогнозувати = час на втілення
}

interface Decision {
  id: string;
  title: string;
  options: string[];     // живі альтернативи, ще на столі
  uncertainty: string;   // який факт чекаємо дізнатися
  trigger: Trigger;
  owner: string;         // хто відповідає, коли настане момент
  adr: string;           // ADR, що фіксує саме відкладання
  // рухомий стан, який веде реєстр:
  status: Status;
  holdCount: number;     // скільки вимірів поспіль трималося спрацювання
}
