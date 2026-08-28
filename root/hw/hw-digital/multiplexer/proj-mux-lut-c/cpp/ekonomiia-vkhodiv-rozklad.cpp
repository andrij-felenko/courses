// Позначення того, у що зводиться функція від останньої змінної c у кожній парі рядків.
typedef enum { IN_0, IN_1, IN_C, IN_NC } mux_din_t;   // 0, 1, c, ¬c

// Розклад f(a,b,c) за молодшою змінною c:
// для кожної адреси (a,b) визначаємо, яку з чотирьох форм дає функція від c.
// Результат — чотири входи даних мультиплексора 4→1 з адресою (a,b).
void decompose_by_c(bool (*f)(bool, bool, bool), mux_din_t din[4]) {
    for (uint32_t ab = 0; ab < 4; ++ab) {
        bool a = (ab >> 1) & 1;
        bool b = (ab >> 0) & 1;
        bool y0 = f(a, b, 0);          // кофактор c=0
        bool y1 = f(a, b, 1);          // кофактор c=1
        if      (!y0 && !y1) din[ab] = IN_0;    // обидва 0  → сталий 0
        else if ( y0 &&  y1) din[ab] = IN_1;    // обидва 1  → сталий 1
        else if (!y0 &&  y1) din[ab] = IN_C;    // 0,1       → дорівнює c
        else                 din[ab] = IN_NC;   // 1,0       → дорівнює ¬c
    }
}

// Обчислення на меншому мультиплексорі: адреса — лише (a,b),
// а обраний вхід за потреби підставляє живе значення c.
bool mux4_eval(const mux_din_t din[4], bool a, bool b, bool c) {
    uint32_t ab = ((uint32_t)a << 1) | (uint32_t)b;   // адреса з двох змінних
    switch (din[ab]) {                                 // "прочитати" обраний вхід
        case IN_0:  return false;
        case IN_1:  return true;
        case IN_C:  return c;
        case IN_NC: return !c;
    }
    return false;
}
