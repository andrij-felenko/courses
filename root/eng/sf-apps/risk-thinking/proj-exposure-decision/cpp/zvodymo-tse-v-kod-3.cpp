static const Risk mono_risks[] = {
    { "База — вузьке місце під навантаженням",     0.50, 20.0 },
    { "Єдина точка відмови (падіння = весь сервіс)", 0.20, 15.0 },
    { "Звіти гальмують основні запити",             0.40,  5.0 },
    { "Міграції болять зі зростанням даних",        0.30,  8.0 },
};

static const Risk cache_risks[] = {
    { "База — вузьке місце (залишковий)",           0.15, 20.0 },
    { "Неузгодженість кешу й бази",                 0.60, 12.0 },
    { "Неправильна інвалідація кешу",               0.50, 10.0 },
    { "Вузол кешу сам падає / переповнюється",      0.40,  6.0 },
    { "Складніше розгортання розподіленого стану",  0.50,  5.0 },
    { "Команда без досвіду з цим кешем",            0.60,  8.0 },
};

static int risk_count(const Risk* arr, size_t bytes) {
    return (int)(bytes / sizeof(Risk));
}

int main() {
    Variant mono  = { "M (моноліт)", mono_risks,
                      risk_count(mono_risks,  sizeof(mono_risks)) };
    Variant cache = { "P (кеш)",     cache_risks,
                      risk_count(cache_risks, sizeof(cache_risks)) };

    double em = total_exposure_naive(mono);
    double ep = total_exposure_naive(cache);

    printf("Експозиція %s: %.1f люд.-днів\n", mono.name,  em);
    printf("Експозиція %s: %.1f люд.-днів\n", cache.name, ep);

    const Variant& winner = (em <= ep) ? mono : cache;
    printf("Вирок: обрати %s (менша сумарна експозиція, різниця %.1f)\n",
           winner.name, (em < ep ? ep - em : em - ep));
    return 0;
}
