// Клас факту диктує міцність читання — не система і не «всюди строго».
type Consistency = "strong" | "eventual";

async function mayOpen(deviceId: string, userId: string): Promise<boolean> {
  // Право відчинити двері читаємо СТРОГО: авторитетне джерело (лідер/кворум).
  const grant = await store.read(`grant:${homeOf(deviceId)}:${userId}`, "strong");
  return grant?.active === true;   // не підтвердили строго (розкол) → «ні»: fail-closed
}

async function latestTemp(deviceId: string): Promise<number | null> {
  // Температуру читаємо ЗРЕШТОЮ: з найближчої репліки, хай трохи застарілу.
  const r = await store.read(`temp:${deviceId}`, "eventual");
  return r?.value ?? null;         // застаріле число нікому не шкодить
}
