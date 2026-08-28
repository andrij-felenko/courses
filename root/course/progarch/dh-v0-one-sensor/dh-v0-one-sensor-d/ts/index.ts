const THRESHOLD = 20.0;          // поріг зашито просто в коді

async function main() {
  while (true) {
    const t = await readSensor();        // драйвер давача → °C
    if (t < THRESHOLD) await heaterOn(); // рішення → дія
    else await heaterOff();
    await sleep(30_000);                 // знову спитати давач за 30 с
  }
}
main();
