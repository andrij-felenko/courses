// Рахунок за місяць для заданої кількості оплачуваних годин.
// hours_billed — скільки годин реально тікає лічильник.
double monthly_cost_usd(double price_per_hour, double hours_billed) {
    return price_per_hour * hours_billed;   // платимо лише за оплачувані години
}

// Скільки активних годин на місяць для сервісу «години на день × дні».
double active_hours(double hours_per_day, double workdays_per_month) {
    return hours_per_day * workdays_per_month;
}
