// npm install serialport
import { SerialPort } from "serialport";
import { ReadlineParser } from "@serialport/parser-readline";

const PORT = "COM7"; // Linux: "/dev/ttyUSB0", macOS: "/dev/cu.SLAB_USBtoUART"
const BAUD = 115200;

const port = new SerialPort({
  path: PORT,
  baudRate: BAUD,
  dataBits: 8,
  parity: "none",
  stopBits: 1,
});

// парсер сам ріже потік на рядки по \n — не доводиться склеювати шматки вручну
const parser = port.pipe(new ReadlineParser({ delimiter: "\n" }));
parser.on("data", (line: string) => console.log(line.trimEnd()));

port.on("open", () => {
  console.log(`Відкрито ${PORT} на ${BAUD} бод.`);
  port.write("status\n"); // надіслати команду пристрою
});
port.on("error", (err) => console.error("Помилка порту:", err.message));
