import { SerialPort } from "serialport";

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

// Вивести SiK-модуль із прозорого режиму в режим команд.
// Ритуал: >1 с тиші → '+++' (без \n) → >1 с тиші → чекай 'OK'.
async function enterCommandMode(port: SerialPort): Promise<boolean> {
  port.flush();                       // викинути телеметрію, що вже натекла
  await sleep(1200);                  // СТОРОЖОВА ПАУЗА до +++ (нічого не шлемо!)
  port.write("+++");                  // рівно три плюси, БЕЗ переведення рядка
  await sleep(1200);                  // СТОРОЖОВА ПАУЗА після +++
  const resp = port.read()?.toString() ?? "";   // модуль відповідає 'OK\r\n'
  return resp.includes("OK");
}

// Послати одну AT/RT-команду (з CR) і зібрати відповідь як текст.
async function at(port: SerialPort, cmd: string, wait = 300): Promise<string> {
  port.flush();
  port.write(cmd + "\r\n");           // команди — З переведенням рядка
  await sleep(wait);
  return (port.read()?.toString() ?? "").trim();
}
