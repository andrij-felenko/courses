type ChangeKind =
  | "add"       // нове поле/значення; старі дані лишаються валідні
  | "reshape"   // існуюче поле переливають у НОВУ форму (новий ключ/стовпець)
  | "remove"    // прибирають стару форму, якою вже не пишуть
  | "redefine"; // тому САМОМУ ключу дають НОВИЙ сенс ← отрута

interface DataChange {
  what: string;               // людський опис
  derived: boolean;           // дані — чиста функція джерела правди?
  rewritable: boolean;        // збережене можна переписати на місці? (false = незмінна історія)
  controlsBothSides: boolean; // читача й писаря деплоїш РАЗОМ?
  kind: ChangeKind;
}

type Strategy =
  | "REBUILD"           // похідне: перерахуй із джерела, без вікна
  | "ADD"               // адитивне: додай поруч, backfill сенсу нема
  | "MIGRATE_IN_PLACE"  // переписуване джерело: expand → backfill → contract
  | "SCHEMA_ON_READ"    // незмінна історія: версіонуй записи, рости декодер
  | "RETIRE"            // прибрати стару форму, коли читачів уже нема
  | "FORBIDDEN";        // перепризначення сенсу живого ключа — не роби

type Window = "none" | "short" | "long" | "grows-with-decoder" | "may-never-close";
type Compat = "n/a" | "backward" | "forward" | "backward+forward";

interface Decision {
  strategy: Strategy;
  window: Window;
  backfill: boolean;   // чи треба чіпати старі рядки
  compat: Compat;
  note: string;
}
