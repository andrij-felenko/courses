// core.ts — ядро на циклі подій: приймає кадри, розгалужує на два шви (рідний дім TS)
import { createServer, Socket } from "node:net";

export type Frame = { deviceId: string; ts: number; value: number };

const actors = new Map<string, DeviceActor>();
function actorFor(id: string): DeviceActor {
  let a = actors.get(id);
  if (!a) actors.set(id, (a = new DeviceActor(id, raiseAlert)));
  return a;
}

createServer((sock: Socket) => {
  sock.setEncoding("utf8");
  let buf = "";
  sock.on("data", (chunk: string) => {
    buf += chunk;
    for (let nl = buf.indexOf("\n"); nl >= 0; nl = buf.indexOf("\n")) {
      const line = buf.slice(0, nl); buf = buf.slice(nl + 1);
      let f: Frame;
      try { f = JSON.parse(line); } catch { continue; }  // биту телеметрію мовчки кидаємо
      actorFor(f.deviceId).post(f);   // ШОВ А: скринька актора — ізольований стан пристрою
      analytics.submit(f);            // ШОВ Б: обмежена черга → пул воркерів (важкий CPU)
    }
  });
  sock.on("error", () => sock.destroy());
}).listen(9099);
