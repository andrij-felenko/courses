// Бітовий запис LSB-first (як у GIF): код width бітів дописуємо до акумулятора.
typedef struct { uint8_t *out; size_t o; uint32_t acc; int nbits; } BitWriter;

void bits_put(BitWriter *bw, int code, int width) {
    bw->acc |= (uint32_t)code << bw->nbits;   // молодші біти коду — першими
    bw->nbits += width;
    while (bw->nbits >= 8) {                   // вивантажуємо повні байти
        bw->out[bw->o++] = (uint8_t)(bw->acc & 0xFF);
        bw->acc >>= 8;
        bw->nbits -= 8;
    }
}
// наприкінці: якщо лишилися біти (nbits>0) — дописати останній неповний байт.
