// Розкладка T568B: пара → контакти 8P8C (нумерація контактів 1..8)
struct Pair568B { const char *pair; uint8_t tip; uint8_t ring; };

static const Pair568B t568b[4] = {
    { "orange", 1, 2 },   // помаранчева:  біло-помаранч / помаранч
    { "green",  3, 6 },   // зелена:       біло-зелена / зелена  (контакти 3 і 6 — НЕ поруч!)
    { "blue",   4, 5 },   // синя:         синя / біло-синя
    { "brown",  7, 8 },   // бура:         біло-бура / бура
};

// Перевірка: чи лежать обидві жили сигналу в ОДНІЙ парі?
bool same_pair(uint8_t a, uint8_t b) {
    for (const auto &p : t568b)
        if ((p.tip == a && p.ring == b) ||
            (p.ring == a && p.tip == b))
            return true;
    return false;   // різні пари → захист звивання втрачено
}
