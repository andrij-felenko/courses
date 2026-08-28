// Контракт межі «хаб ↔ драйвер пристрою». Обидві сторони спираються лише на це.
type Celsius = number;

type Reading =
  | { ok: true;  tempC: Celsius; at: number }        // at — час зчитування, epoch-мс
  | { ok: false; reason: "offline" | "timeout" };     // збій — значення, не виняток

interface DeviceDriver {
  // ПЕРЕДУМОВА:  викликати не частіше, ніж раз на секунду.
  // ПОСТУМОВА:   за справного пристрою — ok:true з tempC у [-40, 85];
  //              інакше ok:false. НІКОЛИ не кидає виняток крізь межу.
  read(): Promise<Reading>;
}
