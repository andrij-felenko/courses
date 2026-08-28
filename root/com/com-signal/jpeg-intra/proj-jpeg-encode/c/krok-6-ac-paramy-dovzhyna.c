static int prevDC = 0;   /* стан між блоками: DC попереднього блока */

static void encode_block(Bits *b, const int Sq[8][8]) {
    const int *flat = &Sq[0][0];
    int z[64];
    for (int k = 0; k < 64; k++) z[k] = flat[ZZ[k]];   /* зигзаг → стрічка */

    /* --- DC: різниця з попереднім блоком → категорія + амплітуда --- */
    int diff = z[0] - prevDC;
    prevDC = z[0];
    int s = category(diff);
    put(b, DC[s].code, DC[s].len);
    if (s) put(b, amplitude(diff, s), s);

    /* --- AC: пари (RUNLENGTH, SIZE) + амплітуда, з EOB і ZRL --- */
    int run = 0;
    for (int k = 1; k < 64; k++) {
        if (z[k] == 0) { run++; continue; }
        while (run > 15) {                       /* серія > 15 нулів → ZRL */
            put(b, AC[0xF0].code, AC[0xF0].len);
            run -= 16;
        }
        int sz  = category(z[k]);
        int sym = (run << 4) | sz;               /* байт RRRRSSSS */
        put(b, AC[sym].code, AC[sym].len);
        put(b, amplitude(z[k], sz), sz);
        run = 0;
    }
    if (run) put(b, AC[0x00].code, AC[0x00].len);   /* хвіст нулів → EOB */
}
