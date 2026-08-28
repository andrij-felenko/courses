import test from "node:test";
import assert from "node:assert/strict";
import { createHmac } from "node:crypto";

const sent: any[] = [];
setNotifier(async (ev) => { sent.push(ev); });     // шпигун замість справжнього пуша

function sign(body: object) {                        // підписуємо, як це робив би провайдер
  const raw = Buffer.from(JSON.stringify(body));
  const t = Math.floor(Date.now() / 1000);
  const v1 = createHmac("sha256", process.env.ACME_WEBHOOK_SECRET!)
    .update(Buffer.concat([Buffer.from(`${t}.`), raw])).digest("hex");
  return { raw, header: `t=${t},v1=${v1}` };
}
const drain = async () => { while (await processOnce()) {} };

test("дубль того самого id — рівно одна обробка", async () => {
  await resetDb(); sent.length = 0;
  const { raw, header } = sign({ id: "e1", device_id: "lock-42", state: "open", seq: 5 });
  assert.equal(await handleWebhook(raw, header), 200);
  assert.equal(await handleWebhook(raw, header), 200);   // провайдер повторив
  assert.equal(await countRows("jobs"), 1);              // у чергу лягло ОДИН раз
  await drain();
  assert.equal((await getTwin("lock-42")).state, "open");
  assert.equal(sent.length, 1);                          // один пуш, не два
});

test("переставлені події — старіша не затирає новішу", async () => {
  await resetDb(); sent.length = 0;
  const a = sign({ id: "e2", device_id: "lock-42", state: "open",   seq: 5 });
  const b = sign({ id: "e3", device_id: "lock-42", state: "closed", seq: 4 }); // старіша!
  await handleWebhook(a.raw, a.header);
  await handleWebhook(b.raw, b.header);
  await drain();
  const twin = await getTwin("lock-42");
  assert.equal(twin.state, "open");                      // seq 4 не перебив seq 5
  assert.equal(twin.seq, 5);
});

test("загублена подія — звірка виправляє дрейф", async () => {
  await resetDb(); sent.length = 0;
  await seedTwin("lock-42", "closed", 5);                // остання відома правда
  // подія seq=6 «відчинено» НЕ дійшла (ендпоінт лежав) — handleWebhook не викликаний
  await reconcileDevice("lock-42", async () => ({ state: "open", seq: 6 }));
  assert.equal((await getTwin("lock-42")).state, "open"); // звірка стягла до джерела
  assert.equal(sent.at(-1)?.state, "open");              // і сповістила про виправлення
});

test("poison-подія — у мертву чергу, решта черги жива", async () => {
  await resetDb(); sent.length = 0;
  const bad  = sign({ id: "e4", device_id: "lock-42", state: "???",  seq: 7 }); // впаде щоразу
  const good = sign({ id: "e5", device_id: "lock-9",  state: "open", seq: 1 });
  await handleWebhook(bad.raw, bad.header);
  await handleWebhook(good.raw, good.header);
  for (let i = 0; i < MAX_ATTEMPTS; i++) { await forceReady(); await drain(); } // без чекання
  assert.equal(await countRows("dead_letter"), 1);       // отруйна осіла в DLQ
  assert.equal((await getTwin("lock-9")).state, "open"); // здорова пройшла попри отруту поряд
  assert.equal(await countRows("jobs"), 0);              // черга чиста
});
