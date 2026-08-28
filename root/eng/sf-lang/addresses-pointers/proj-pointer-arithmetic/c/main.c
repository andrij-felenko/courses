// обхід масиву: крок в ЕЛЕМЕНТАХ, межа — строго <
for (int* p = arr; p < arr + n; ++p)   // arr+n — «за останнім», порівнювати можна
    sum += *p;                          // *(arr+i) ≡ arr[i]

// перетлумачити 4 байти як float — НЕ через (float*), а копією
uint8_t buf[4] = {...};
float f;
memcpy(&f, buf, sizeof f);              // переносно, без UB і без вимог вирівнювання

// байт vs елемент: memcpy міряє в БАЙТАХ
memcpy(dst, src, n * sizeof *src);      // n елементів = n*sizeof байтів (НЕ просто n)
