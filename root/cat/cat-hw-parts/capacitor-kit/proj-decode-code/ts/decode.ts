// decode.ts — розкодовувач маркування конденсатора
// вхід: те, що надруковано на корпусі; вихід: ємність у пФ + допуск + напруга

interface Reading {
  picofarads: number;      // ємність, зведена до пФ (спільна валюта)
  tolerancePct: number | null;  // ±% з літери, або null
  voltage: number | null;  // робоча напруга у В, якщо вказана
}

// літера-допуск → відсоток (у число ємності НЕ входить)
const TOLERANCE: Record<string, number | null> = {
  B: 0.1, C: 0.25, D: 0.5, F: 1, G: 2,
  J: 5, K: 10, M: 20, Z: null, // Z = +80/−20 %, несиметричний
};
// суфікс одиниці → у скільки пікофарад (ключі — уже у верхньому регістрі)
const UNIT_PF: Record<string, number> = {
  P: 1, N: 1_000, U: 1_000_000, M: 1_000_000_000,
};

export function toPicofarads(mark: string): Reading {
  // мікрознак µ/μ → ASCII "u" ДО toUpperCase(), далі весь рядок — у верхньому регістрі
  let s = mark.trim().replace(/[µμ]/g, "u").toUpperCase().replace(/\s+/g, "");

  // 1. Відрізати робочу напругу: "104/50V", "0.1UF63V"
  let voltage: number | null = null;
  const vm = s.match(/(\d+(?:\.\d+)?)V\b/);
  if (vm) {
    voltage = parseFloat(vm[1]);
    s = (s.slice(0, vm.index!) + s.slice(vm.index! + vm[0].length)).replace(/^[/ ]+|[/ ]+$/g, "");
  }

  // 2. Відрізати літеру-допуск у кінці: "104J" → код "104", ±5 %
  let tolerancePct: number | null = null;
  const tm = s.match(/([BCDFGJKMZ])$/);
  if (tm && !/[UNP]$/.test(s.slice(0, tm.index!))) { // не сплутати з одиницею
    tolerancePct = TOLERANCE[tm[1]];
    s = s.slice(0, tm.index!);
  }

  // 3. Гілка ПРЯМОГО маркування: крапка/кома або буква-одиниця (µ уже → U вище)
  const hasUnit = /[PNUM]/.test(s.replace(/F$/, "").replace(/\d/g, ""));
  if (s.includes(".") || s.includes(",") || hasUnit) {
    s = s.replace(",", ".");

    // форма "4N7"/"2U2": буква-одиниця замість десяткової крапки
    const embedded = s.match(/^(\d*)([PNUM])(\d+)$/);
    if (embedded) {
      const value = parseFloat(`${embedded[1] || "0"}.${embedded[3]}`);
      return { picofarads: value * UNIT_PF[embedded[2]], tolerancePct, voltage };
    }
    // форма "470UF"/"100N"/"0.1": число + необовʼязкова одиниця
    const plain = s.match(/^(\d+(?:\.\d+)?)([PNUM]?)F?$/);
    if (plain) {
      const value = parseFloat(plain[1]);
      const unit = plain[2] || "U"; // без одиниці велика деталь = мкФ
      return { picofarads: value * UNIT_PF[unit], tolerancePct, voltage };
    }
  }

  // 4. Гілка ТРИЦИФРОВОГО коду: рівно 3 цифри "XYZ" → XY × 10^Z пФ
  if (/^\d{3}$/.test(s)) {
    const significant = parseInt(s.slice(0, 2), 10);
    const exponent = parseInt(s[2], 10);
    return { picofarads: significant * 10 ** exponent, tolerancePct, voltage };
  }

  // 5. Один-два знаки — це пФ як є ("47" = 47 пФ)
  if (/^\d{1,2}$/.test(s)) {
    return { picofarads: parseFloat(s), tolerancePct, voltage };
  }

  throw new Error(`не розпізнав маркування: ${JSON.stringify(mark)}`);
}

export function human(pf: number): string {
  const trim = (x: number) => parseFloat(x.toFixed(6)).toString();
  if (pf >= 1_000_000) return `${trim(pf / 1_000_000)} мкФ`;
  if (pf >= 1_000) return `${trim(pf / 1_000)} нФ`;
  return `${trim(pf)} пФ`;
}

for (const mark of ["104", "223", "474", "0.1", "470uF 25V", "4n7", "104J", "100", "47"]) {
  const { picofarads, tolerancePct, voltage } = toPicofarads(mark);
  const extra = (tolerancePct ? `, ±${tolerancePct}%` : "") + (voltage ? `, ${voltage} В` : "");
  console.log(`${mark.padStart(10)}  →  ${human(picofarads).padStart(10)}   (${picofarads} пФ${extra})`);
}
