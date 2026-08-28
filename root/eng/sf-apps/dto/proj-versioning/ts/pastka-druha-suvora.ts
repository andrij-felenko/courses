import { z } from "zod";

// ПАСТКА: суворий до ФОРМИ валідатор — забороняє будь-яке незнайоме поле.
const OrderStrict = z.object({
  id:    z.number().int().positive(),
  total: z.number().nonnegative(),
}).strict();                    // ← .strict(): невідоме поле = помилка

// Сьогодні працює. А завтра сервер додав промо-банер:
OrderStrict.parse({ id: 42, total: 9, promo_banner: "-20%" });
//                                     ^^^^^^^^^^^^
// КИДАЄ: Unrecognized key(s) in object: 'promo_banner'
// Старий клієнт не може прочитати НАВІТЬ id і total, які чудово знає,
// бо вдавився полем, до якого йому й діла немає.
