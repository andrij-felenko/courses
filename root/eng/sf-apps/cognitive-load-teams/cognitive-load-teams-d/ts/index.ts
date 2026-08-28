// Стороннє глушить внутрішнє: логіку знижки видно ледве
function finalPrice(o: Order): number {
    // ручне складання конфігу з трьох джерел просто щоб дізнатися ставку
    let tier = process.env.DISCOUNT_TIER ?? readFile("/etc/app/tier.conf");
    if (!tier) tier = queryDb("SELECT tier FROM cfg LIMIT 1");
    const rate = Number(tier);            // а раптом не число — буде NaN
    // ще й ручний перерахунок валюти вкраплено в ту саму функцію
    const usd = o.amount * fetchRate(o.ccy); // мережевий виклик усередині ціни
    return usd - usd * rate;              // ← а ось це і є вся суть
}
