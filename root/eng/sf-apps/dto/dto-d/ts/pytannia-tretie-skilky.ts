// Вихід: усе присутнє, обчислене, тільки для читання
interface OrderResponse {
  readonly id: number;          // сервер завжди знає id
  readonly total: number;       // ПОРАХОВАНО доменом
  readonly status: string;
  readonly lines: LineView[];
}

// Вхід на СТВОРЕННЯ: id ще нема, total слати НЕ можна
interface CreateOrderRequest {
  readonly lines: LineInput[];  // самий намір; більш нічого клієнт не диктує
  // жодного id, жодного total — їх дасть/порахує сервер
}

// Вхід на РЕДАГУВАННЯ: усе optional — «прийшло тільки те, що міняємо»
interface PatchOrderRequest {
  readonly status?: string;     // є → зміни; нема → не чіпай
  readonly lines?: LineInput[];
}
