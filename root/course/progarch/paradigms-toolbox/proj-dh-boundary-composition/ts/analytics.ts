// analytics.ts — той самий шов у Node: обмежена черга перед пулом worker_threads
import { Worker } from "node:worker_threads";
import os from "node:os";
import { Frame } from "./core";

const CAP = 256;                                    // ШОВ Б: місткість черги
const queue: Frame[] = [];
const pool = Array.from({ length: os.cpus().length }, () => new Worker("./score.js"));
const idle = [...pool];

export const analytics = {
  submit(f: Frame): boolean {
    if (queue.length >= CAP) return false;          // повно → політика вирішує тут
    queue.push(f); pump(); return true;
  },
};

function pump(): void {
  while (idle.length && queue.length) {
    const w = idle.pop()!, f = queue.shift()!;
    w.once("message", (v) => { rules.post(v); idle.push(w); pump(); }); // ШОВ В → правила
    w.postMessage(f);                               // важкий CPU — на окремому потоці V8
  }
}
