// billing.ts
export const settings = { feeRate: 0.02, graceDays: 3, periodDays: 30 }; // глобал 1: конфіг
export let renewalsTotal = 0;                                            // глобал 2: лічильник
const log = console;                                                     // глобал 3: логер

export function renew(sub: Subscription): Renewal {
  const now = new Date();                                                // глобал 4: годинник
  const deadline = addDays(sub.paidUntil, settings.graceDays);
  if (now.getTime() > deadline.getTime()) {
    log.warn(`sub ${sub.id}: пільговий строк вичерпано`);
    return { status: "expired", amount: 0, paidUntil: sub.paidUntil };
  }
  const amount = Math.round(sub.planPrice * (1 + settings.feeRate) * 100) / 100;
  sub.paidUntil = addDays(now, settings.periodDays);
  renewalsTotal += 1;
  log.info(`sub ${sub.id}: продовжено на ${amount.toFixed(2)}`);
  return { status: "ok", amount, paidUntil: sub.paidUntil };
}
