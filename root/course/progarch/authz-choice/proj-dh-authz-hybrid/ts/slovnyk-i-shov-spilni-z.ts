type Role   = "owner" | "resident" | "guest";
type Action = "unlock" | "lock" | "view" | "configure";

// Ті самі User/Resource. Новина одна: роль у домі їде РАЗОМ з автентифікованим
// користувачем (локальний факт із токена), а не тягнеться портом, як в А.
interface User     { id: string; roleInHome: Record<string, Role | undefined>; }
interface Resource { homeId: string; }

// ШОВ — байт-у-байт той самий, що у Варіанті А: can асинхронний.
// Саме тому підміна А ⇄ гібрид лишається двобічною — підпис не змінився.
interface Authorizer {
  can(user: User, action: Action, resource: Resource): Promise<boolean>;
}
