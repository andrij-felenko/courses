// беззнакове a + b  (wrap визначений, але все одно небажаний)
if (a > UINT_MAX - b)
    overflow();              // суму НЕ рахуємо
else
    sum = a + b;

// знакове a + b  (переповнення = UB → ловимо обидві межі)
if (b > 0 && a > INT_MAX - b)      overflow();   // переб'є зверху
else if (b < 0 && a < INT_MIN - b) overflow();   // провалиться знизу
else                               sum = a + b;
