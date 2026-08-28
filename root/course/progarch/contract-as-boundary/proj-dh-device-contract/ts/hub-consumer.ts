// hub-consumer.ts — споживач, що спирається ЛИШЕ на I-1..I-6 і ні на що поза ними.
import type { DeviceDriver, Fault } from "./device-driver.ts";

const MIN_PERIOD_MS = 1_000;                     // I-5: не частіше 1/с — НАШ борг

function label(reason: Fault): string {
  switch (reason) {                              // I-3: множина ЗАКРИТА → розбір вичерпний
    case "offline": return "пристрій офлайн";
    case "timeout": return "пристрій не встиг";
    default: { const _never: never = reason; return _never; }  // забудеш гілку — не збереться
  }
}

async function poll(driver: DeviceDriver, show: (s: string) => void): Promise<void> {
  const r = await driver.read();                 // I-3: воно не кине — обробляємо ЗНАЧЕННЯ
  if (!r.ok) {
    show(label(r.reason));
  } else {
    // I-1+I-2: tempC — це °C у [−40,85]. Формат — НАШ, на межі: I-6 мовчить про точність,
    // тож кількість знаків драйвера ми НЕ пускаємо назовні, а нав'язуємо свою.
    show(`${r.tempC.toFixed(1)} °C`);
  }
  // I-6: період НЕ гарантовано → розклад ведемо від СВОГО годинника, а не з r.at
  // (вивести період із at — то опертися на випадковість, тобто на кільце Гайрама).
  setTimeout(() => poll(driver, show), MIN_PERIOD_MS);
}
