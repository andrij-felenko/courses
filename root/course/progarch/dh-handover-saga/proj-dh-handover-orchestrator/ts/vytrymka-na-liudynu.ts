class WaitingForHuman extends Error { constructor(public until: number) { super("waiting"); } }
const DAY = 86_400_000;

async function waitForNewOwner(ctx: Ctx): Promise<void> {
  await postClaimInvite(ctx.homeId, ctx.idemKey);       // запросити нових (ідемпотентно)
  if (await claimAccepted(ctx.homeId)) return;          // уже підтвердили → крок завершено
  throw new WaitingForHuman(Date.now() + 7 * DAY);      // ще ні → паркуємось, не падаємо
}

// нові власники підтвердили → будимо вперед
async function onClaim(p: Ports, id: string, steps: Step[]): Promise<void> {
  const s = await p.load(id);
  if (s.status !== "waiting") return;                   // ідемпотентно: пізній клац — тиша
  s.status = "running"; await p.persist(s); await drive(p, id, steps);
}
// витримку вичерпано → невдача ДО півота: cursor лишається на awaitClaim (запрошення живе)
async function onClaimDeadline(p: Ports, id: string, steps: Step[]): Promise<void> {
  const s = await p.load(id);
  if (s.status !== "waiting" || Date.now() < (s.deadline ?? Infinity)) return;
  s.status = "running"; s.dir = "back";                 // задкуємо, відкликаючи і cancelClaim
  await p.persist(s); await drive(p, id, steps);
}
