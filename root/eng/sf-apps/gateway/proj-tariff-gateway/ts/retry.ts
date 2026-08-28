// http/retry.ts — повтор ЛИШЕ тимчасового, з експоненційним відкатом + jitter.
import { МережевийЗбій } from "./transport";

const сон = (мс: number) => new Promise(r => setTimeout(r, мс));

export async function зПовтором<T>(
  спроба: () => Promise<T>, разів = 3, базоваМс = 200,
): Promise<T> {
  for (let n = 0; ; n++) {
    try {
      return await спроба();
    } catch (e) {
      // повторюємо ЛИШЕ тимчасове; усе інше (доменні помилки) — кидаємо далі
      const тимчасове = e instanceof МережевийЗбій;
      if (!тимчасове || n >= разів - 1) throw e;
      const пауза = базоваМс * 2 ** n * (0.5 + Math.random() * 0.5);  // відкат + jitter
      await сон(пауза);
    }
  }
}
