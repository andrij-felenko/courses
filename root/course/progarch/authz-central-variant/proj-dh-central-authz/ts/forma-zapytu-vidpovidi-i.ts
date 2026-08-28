type Role   = "owner" | "resident" | "guest";
type Action = "unlock" | "lock" | "view" | "configure";

interface User     { id: string; }
interface Resource { kind: string; id: string; homeId: string; } // ЗАВАНТАЖЕНИЙ об'єкт: homeId — з нашої БД

// Форма запиту рішення — маленький документ, що їде за межу процесу.
interface DecisionRequest {
  subject:  string;                 // хто — з автентифікованої сесії, НЕ з тіла запиту
  action:   Action;                 // що — з маршруту
  resource: string;                 // над чим — "door:42"
  context:  Record<string, string>; // факти для рішення — лише з авторитетного джерела
}
// Відповідь: вердикт + причина (у журнал) + дім, на якому вердикт тримався (для кеша — нижче).
interface DecisionResponse { allow: boolean; reason: string; home?: string; }

// Клієнт до центру: саме він згодом сховає мережу, дедлайн, запобіжник і fail-closed.
interface PdpClient { check(req: DecisionRequest): Promise<DecisionResponse>; }

// ШОВ — той самий інтерфейс, що у Варіанті А. Обробники не бачать, що рішення поїхало в центр.
interface Authorizer {
  can(user: User, action: Action, resource: Resource): Promise<boolean>;
}
