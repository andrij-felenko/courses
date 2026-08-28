// Кожен запис несе СВОЮ версію форми; сенс wh читається ЗА ВЕРСІЄЮ, не вгадується.
interface RawRecord { schema: number; [k: string]: unknown; }
interface Reading { wattHours: number; }   // канонічна форма читача

function decode(r: RawRecord): Reading {
  switch (r.schema) {
    case 1: return decodeV1(r);   // wh відсутнє: лише миттєве w — інтегруємо самі
    case 2: return decodeV2(r);   // wh = НАКОПИЧУВАЛЬНИЙ лічильник (Вт·год від старту)
    case 3: return decodeV3(r);   // wh = ДЕЛЬТА за інтервал ← НОВИЙ сенс, НОВА версія
    default: throw new Error(`нема декодера для schema:${r.schema}`);
  }
}
