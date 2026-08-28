// readonly скрізь: зібрали — застигло. Хочеш інше — новий об'єкт.
interface OrderDto {
  readonly id: number;
  readonly total: number;
  readonly status: string;
  readonly lines: readonly LineDto[];   // і вкладене теж незмінне
}

// Дві копії з однаковими полями — цілком взаємозамінні: тотожності нема.
const a: OrderDto = { id: 42, total: 100, status: "paid", lines: [] };
const b: OrderDto = { id: 42, total: 100, status: "paid", lines: [] };
// питати «котрий із них справжній Order?» — безглуздо: обидва — лише виписки
