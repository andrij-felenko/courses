// e2e-smoke.ts — жене справжнє значення від HTTP-краю крізь усі вузли й СТВЕРДЖУЄ вихід.
// Стукає ПО МЕРЕЖІ в уже розгорнуту нитку (реальний брокер), не імпортує її функцій.
const BASE = process.env.SMOKE_URL ?? "http://localhost:8080";

// (1) Унікальне значення на КОЖЕН прогін: так ми читаємо СВІЙ запис, а не леглий
// з минулого разу. Якби слали стале число, тест зеленів би й на мертвій нитці.
const sent = String(1000 + Math.floor(Math.random() * 9000));

async function main() {
  // (2) справжній вхід у ПЕРШИЙ вузол — HTTP-край
  const post = await fetch(`${BASE}/temp`, { method: "POST", body: sent });
  if (!post.ok) throw new Error(`POST дав ${post.status}`);

  // (3) ОПИТУЄМО останній край, поки значення пройде API → брокер → воркер → сховище.
  // Опитування з дедлайном, а не фіксований сон: система асинхронна, і час
  // проходу нитки — величина плавуча, а не константа.
  const deadline = Date.now() + 10_000;
  while (Date.now() < deadline) {
    const got = await fetch(`${BASE}/temp`);
    if (got.ok && (await got.text()).trim() === sent) {
      console.log(`нитка пройшла наскрізь: ${sent} повернулось із іншого краю`);
      return; // СТВЕРДЖЕННЯ справдилось: дочекались саме НАШОГО значення
    }
    await new Promise((r) => setTimeout(r, 200));
  }
  throw new Error(`нитка не пройшла: ${sent} не з'явилось на іншому краї`);
}

main().catch((e) => { console.error("ДИМОВИЙ ТЕСТ ЧЕРВОНИЙ:", e.message); process.exit(1); });
