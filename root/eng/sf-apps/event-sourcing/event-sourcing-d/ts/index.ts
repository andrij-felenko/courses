// Подія — доконаний факт. Проста незмінна структура: що сталося і на скільки.
type AccountEvent =
  | { kind: "Deposited"; amount: number }
  | { kind: "Withdrawn"; amount: number };

type Account = { balance: number };

const EMPTY: Account = { balance: 0 };          // нульовий стан — з нього все починається

// apply: узяти стан і ОДНУ подію, повернути НАСТУПНИЙ стан. Без побічних ефектів.
function apply(state: Account, e: AccountEvent): Account {
  switch (e.kind) {
    case "Deposited": return { balance: state.balance + e.amount };
    case "Withdrawn": return { balance: state.balance - e.amount };
  }
}

// Поточний стан = згортка ВСІХ подій від порожнього. Ось і вся «база».
function replay(events: AccountEvent[]): Account {
  return events.reduce(apply, EMPTY);
}
