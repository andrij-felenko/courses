const HYSTERESIS = 0.5;              // °C — ширина смуги понад поріг (з кроку про порт)

interface Reading { readonly celsius: number; readonly ok: boolean; }  // з v1
interface Config  { readonly threshold: number; }
interface Device  { readonly kind: string; readonly room: string; readonly state: string; }

function decide(r: Reading, cfg: Config, heating: boolean): boolean {
  if (!r.ok) return false;                                    // давач мовчить → спокій (як v1)
  if (heating) return r.celsius < cfg.threshold + HYSTERESIS; // гріємо — тримаємо смугу
  return r.celsius < cfg.threshold;                           // ще ні — вмикаємо під порогом
}
