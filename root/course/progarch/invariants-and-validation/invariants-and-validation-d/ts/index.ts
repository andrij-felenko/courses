// Об'єкт-значення: конструктор приватний, єдині двері — parse().
class Celsius {
  private constructor(public readonly value: number) {}

  static parse(raw: unknown): Celsius | Error {
    if (typeof raw !== "number" || Number.isNaN(raw))
      return new Error("температура — не число");
    if (raw < -50 || raw > 80)
      return new Error(`температура поза межами: ${raw}`);
    return new Celsius(raw);          // ЄДИНЕ місце, де Celsius народжується
  }
}

// Ядро бере Celsius, а не number — недійсне значення сюди не втрапить.
function decideHeating(room: Celsius, target: Celsius): boolean {
  return room.value < target.value;   // жодної повторної перевірки
}
