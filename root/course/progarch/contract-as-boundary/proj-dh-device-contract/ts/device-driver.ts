// device-driver.ts — АРТЕФАКТ КОНТРАКТУ межі «хаб ↔ драйвер пристрою».
// Обидві сторони імпортують САМЕ цей файл і спираються лише на нього.
export type Celsius = number;

// Збій межі — завжди одне з ЦИХ значень, і не інше (множина ЗАКРИТА).
export type Fault = "offline" | "timeout";

// DTO показу — розрізнене об'єднання: успіх АБО типізований збій-як-значення.
export type Reading =
  | { ok: true;  tempC: Celsius; at: number }   // at — момент зчитування, epoch-МС
  | { ok: false; reason: Fault };

// Команда звітує так само — значенням, не винятком.
export type Ack =
  | { ok: true }
  | { ok: false; reason: Fault };

export interface DeviceDriver {
  read(): Promise<Reading>;                 // читання заліза — асинхронне
  setTarget(tempC: Celsius): Promise<Ack>;  // команда: виставити цільову t°
}
