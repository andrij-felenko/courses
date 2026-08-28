// Стороннє глушить внутрішнє: логіку знижки видно ледве
double finalPrice(const Order& o) {
    // ручне складання конфігу з трьох джерел просто щоб дізнатися ставку
    const char* env = getenv("DISCOUNT_TIER");
    std::string tier = env ? env : readFile("/etc/app/tier.conf");
    if (tier.empty()) tier = queryDb("SELECT tier FROM cfg LIMIT 1");
    double rate = std::stod(tier);           // а раптом не число — впаде тут
    // ще й ручний перерахунок валюти вкраплено в ту саму функцію
    double usd = o.amount * fetchRate(o.ccy); // мережевий виклик усередині ціни
    return usd - usd * rate;                  // ← а ось це і є вся суть
}
