// aggregate.worker.ts — окремий потік V8, справжня паралельність
import { parentPort, workerData } from "node:worker_threads";
import { aggregateMonth } from "./aggregate";
parentPort!.postMessage(aggregateMonth(workerData.hubId, workerData.rows));

// ── server.ts — віддаємо завдання потокові й чекаємо результат ──
import { Worker } from "node:worker_threads";

function aggregateOffloaded(hubId: string, rows: Reading[]): Promise<Summary> {
  return new Promise((resolve, reject) => {
    const w = new Worker(new URL("./aggregate.worker.js", import.meta.url),
                         { workerData: { hubId, rows } });
    w.once("message", (m) => { resolve(m as Summary); w.terminate(); });
    w.once("error", reject);
  });
}

async function handleControl(cmd: string[]) {
  if (cmd[0] === "aggregate") {
    const rows = await storage.month(cmd[1]);
    return await aggregateOffloaded(cmd[1], rows);   // смуга вільна, поки потік меле
  }
}
