import { createServer, Socket } from "node:net";
import { createInterface } from "node:readline";

// асинхронний клієнт черги/БД: await storage.put(...) — теж по мережі
declare const storage: { put(r: unknown): Promise<void> };

createServer((sock: Socket) => {
  const hub = sock.remoteAddress;
  const lines = createInterface({ input: sock });   // рядок за рядком
  lines.on("line", async (raw) => {
    const line = raw.trim();
    if (!line) return;
    let reading: Record<string, unknown>;
    try { reading = JSON.parse(line); }             // дрібний JSON — швидко
    catch { return; }                                // биту телеметрію кидаємо
    reading.hub = hub;
    await storage.put(reading);                      // await → смуга вільна, поки пише
  });
  sock.on("error", () => sock.destroy());
}).listen(9099);
