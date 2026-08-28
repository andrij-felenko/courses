// http/transport.ts — сира розмова з мережею + таймаут. Про тарифи не знає.
export class МережевийЗбій extends Error {}   // обрив, таймаут — тимчасове

export interface СираВідповідь { статус: number; тіло: () => Promise<any>; }

export async function httpGet(
  url: string, токен: string, таймаутМс = 3000,
): Promise<СираВідповідь> {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), таймаутМс);   // таймаут: не висіти вічно
  try {
    const r = await fetch(url, {
      headers: { Authorization: `Bearer ${токен}` },
      signal: ctrl.signal,
    });
    return { статус: r.status, тіло: () => r.json() };
  } catch (e) {
    // обрив зʼєднання або спрацював таймаут — це ТИМЧАСОВЕ, кандидат на повтор
    throw new МережевийЗбій(String(e));
  } finally {
    clearTimeout(t);
  }
}
