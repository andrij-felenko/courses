// Підбір хобі-серва за навантаженням: чи вистачить моменту із запасом.
// Момент = сила · плече (кг·см); паспорт зводимо до робочої напруги
// й ділимо на derate (=2) — поправка на оптимістичний паспорт і розкид.

interface SpecPoint { volts: number; torqueKgcm: number; }

interface Servo {
  name: string;
  spec: SpecPoint[];       // 1+ паспортних точок «напруга → момент»
  workVolts: number;       // напруга, якою реально живимо
}

interface Load {
  forceKgf: number;        // сила на тязі, кгс (важкий випадок)
  armCm: number;           // плече рога від осі вала, см
  safety?: number;         // запас на навантаження (типово 2)
  derate?: number;         // ділник паспорта серва (типово 2)
}

// Лінійна інтерполяція/екстраполяція паспорта на робочу напругу.
function torqueAt(spec: SpecPoint[], volts: number): number {
  const pts = [...spec].sort((a, b) => a.volts - b.volts);
  if (pts.length === 1) return pts[0].torqueKgcm;
  // затиснемо між крайніми точками, далі не екстраполюємо оптимістично
  const lo = pts[0], hi = pts[pts.length - 1];
  const v = Math.max(lo.volts, Math.min(hi.volts, volts));
  for (let i = 0; i < pts.length - 1; i++) {
    const a = pts[i], b = pts[i + 1];
    if (v >= a.volts && v <= b.volts) {
      const t = (v - a.volts) / (b.volts - a.volts);
      return a.torqueKgcm + t * (b.torqueKgcm - a.torqueKgcm);
    }
  }
  return hi.torqueKgcm;
}

function pickServo(load: Load, servo: Servo) {
  const safety = load.safety ?? 2;
  const derate = load.derate ?? 2;

  const needed = load.forceKgf * load.armCm;      // потрібний момент
  const target = needed * safety;                  // з запасом на навантаження
  const paper = torqueAt(servo.spec, servo.workVolts);
  const usable = paper / derate;                   // на що реально кладемось

  return {
    neededKgcm: round(needed),
    targetKgcm: round(target),
    paperKgcm: round(paper),
    usableKgcm: round(usable),
    ok: usable >= target,
    margin: round(usable / target),                // фактичний запас понад ціль
  };
}

const round = (x: number) => Math.round(x * 100) / 100;

// --- застосування: кермо машинки 1:10 на розі LF-20MG, живлення 6 В ---
const lf20mg: Servo = {
  name: "Power HD LF-20MG",
  spec: [{ volts: 4.8, torqueKgcm: 16.5 }, { volts: 6.6, torqueKgcm: 20.0 }],
  workVolts: 6.0,
};
const steering: Load = { forceKgf: 2.5, armCm: 1.5 };

const r = pickServo(steering, lf20mg);
console.log(r);
// { neededKgcm: 3.75, targetKgcm: 7.5, paperKgcm: 18.83,
//   usableKgcm: 9.42, ok: true, margin: 1.26 }
// потрібно 7.5 з запасом; реально доступно ~9.4 → проходить, ще й з запасом ×1.26
