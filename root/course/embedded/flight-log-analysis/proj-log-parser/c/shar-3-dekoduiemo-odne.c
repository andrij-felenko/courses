// Прочитати little-endian ціле шириною n байтів (n ≤ 8) як беззнакове.
static uint64_t rd_uN(const uint8_t *p, int n) {
    uint64_t v = 0;
    for (int i = 0; i < n; i++)
        v |= (uint64_t)p[i] << (8 * i);   // байт [0] — молодший: явний LE
    return v;
}

// Декодувати ОДНЕ поле типу `t` з байтів `p`.
// Значення кладемо в *out (як double); повертаємо РОЗМІР поля в байтах
// (= крок курсора). Так пастка різних розмірів розв'язується сама собою.
static int decode_field(char t, const uint8_t *p, double *out) {
    switch (t) {
    case 'b': *out = (double)(int8_t) p[0];              return 1;
    case 'B': *out = (double)(uint8_t)p[0];              return 1;
    case 'M': *out = (double)(uint8_t)p[0];              return 1;
    case 'h': *out = (double)(int16_t) rd_uN(p, 2);      return 2;
    case 'H': *out = (double)(uint16_t)rd_uN(p, 2);      return 2;
    case 'i': *out = (double)(int32_t) rd_uN(p, 4);      return 4;
    case 'I': *out = (double)(uint32_t)rd_uN(p, 4);      return 4;
    case 'q': *out = (double)(int64_t) rd_uN(p, 8);      return 8;
    case 'Q': *out = (double)(uint64_t)rd_uN(p, 8);      return 8;
    case 'L': *out = (double)(int32_t) rd_uN(p, 4) / 1e7; return 4;  // 1e7° → °
    case 'f': {                                          // 4 байти → float
        uint32_t bits = (uint32_t)rd_uN(p, 4);
        float fv; memcpy(&fv, &bits, 4);                 // біти → float
        *out = (double)fv;                               return 4;
    }
    case 'd': {                                          // 8 байтів → double
        uint64_t bits = rd_uN(p, 8);
        double dv; memcpy(&dv, &bits, 8);
        *out = dv;                                       return 8;
    }
    // застарілі масштабовані: значення = ціле / 100
    case 'c': *out = (double)(int16_t) rd_uN(p, 2) / 100.0; return 2;
    case 'C': *out = (double)(uint16_t)rd_uN(p, 2) / 100.0; return 2;
    case 'e': *out = (double)(int32_t) rd_uN(p, 4) / 100.0; return 4;
    case 'E': *out = (double)(uint32_t)rd_uN(p, 4) / 100.0; return 4;
    // текстові поля — пропускаємо, повертаючи їхній розмір (курсор іде далі)
    case 'n': return 4;
    case 'N': return 16;
    case 'Z': return 64;
    default:  return 0;   // невідомий символ — сигнал «щось не так»
    }
}
