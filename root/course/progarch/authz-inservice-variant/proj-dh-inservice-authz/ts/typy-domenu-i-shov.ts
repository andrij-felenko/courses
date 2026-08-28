type Role   = "owner" | "resident" | "guest";
type Action = "unlock" | "lock" | "view" | "configure";

interface User     { id: string; }
interface Resource { homeId: string; }   // будь-що з приналежністю до дому: замок, камера…

// ШОВ: усі обробники бачать ЛИШЕ це. can асинхронний з першого дня (див. нижче — навіщо).
interface Authorizer {
  can(user: User, action: Action, resource: Resource): Promise<boolean>;
}

// ПОРТ до членства: «яка роль у цього користувача В ЦЬОМУ домі?».
// Ключ — homeId; іншого способу спитати роль тут просто нема.
interface Memberships {
  roleIn(userId: string, homeId: string): Promise<Role | undefined>;
}
