interface PolicyBundle {
  version: string;                                   // ревізія (для 304 і аудиту)
  actionsByRole: Record<Role, Action[]>;             // базова таблиця «роль → дозволені дії»
  guestUnlock: { fromHour: number; toHour: number }; // гість відчиняє лише у денному вікні
}

interface EvalInput { action: Action; role?: Role; isMember: boolean; now: number; }
interface Policy    { version: string; evaluate(x: EvalInput): boolean; }

const HOUR = 3_600_000;

// Компіляція бандла у ЧИСТИЙ оцінювач: жодного I/O, лише обчислення. Одне місце правила.
function compilePolicy(b: PolicyBundle): Policy {
  const table: Record<Role, ReadonlySet<Action>> = {
    owner:    new Set(b.actionsByRole.owner),
    resident: new Set(b.actionsByRole.resident),
    guest:    new Set(b.actionsByRole.guest),
  };
  return {
    version: b.version,
    evaluate({ action, role, isMember, now }) {
      if (!isMember) return false;                   // «член дому» — обов'язкова умова (у центрі!)
      if (!role) return false;                       // нема ролі в цьому домі → ні
      if (table[role].has(action)) return true;      // базовий дозвіл ролі
      if (role === "guest" && action === "unlock") { // спец-правило гостя: денне вікно
        const h = Math.floor((now / HOUR) % 24);
        return h >= b.guestUnlock.fromHour && h < b.guestUnlock.toHour;
      }
      return false;                                  // усе, чого не виписано, — заборонено
    },
  };
}
