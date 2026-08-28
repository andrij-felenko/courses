// Відновлює ОДИН відлік із 4-бітного коду. Дзеркало серединки кодера.
static int16_t adpcm_decode_sample(adpcm_state *s, uint8_t code) {
    int32_t step = step_table[s->index];

    int32_t vpdiff = step >> 3;                 // та сама формула, що в кодері
    if (code & 4) vpdiff += step;
    if (code & 2) vpdiff += step >> 1;
    if (code & 1) vpdiff += step >> 2;
    if (code & 8) s->predict -= vpdiff;
    else          s->predict += vpdiff;

    if (s->predict >  32767) s->predict =  32767;
    if (s->predict < -32768) s->predict = -32768;

    s->index += index_table[code];
    if (s->index < 0)  s->index = 0;
    if (s->index > 88) s->index = 88;

    return (int16_t)s->predict;
}

// Розпаковує N/2 байтів у N відліків. out мусить мати count відліків.
void adpcm_decode(adpcm_state *s, const uint8_t *in, int16_t *out, int count) {
    int i = 0;
    while (i + 1 < count) {
        uint8_t byte = *in++;
        out[i]     = adpcm_decode_sample(s, byte & 0x0f);   // МОЛОДШИЙ — перший
        out[i + 1] = adpcm_decode_sample(s, byte >> 4);     // СТАРШИЙ — другий
        i += 2;
    }
    if (i < count) {                 // непарний хвіст: лише молодший півбайт
        uint8_t byte = *in++;
        out[i] = adpcm_decode_sample(s, byte & 0x0f);
    }
}
