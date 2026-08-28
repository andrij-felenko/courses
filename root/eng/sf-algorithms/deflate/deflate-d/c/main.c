// серце декодера DEFLATE: out[] — уже відновлені байти, pos — їх кількість
int sym = decode_symbol(&bits, &lit_tree);   // код першим деревом
if (sym < 256) {
    out[pos++] = (unsigned char)sym;          // літера — просто пишемо
} else if (sym == 256) {
    break;                                     // 256 — кінець блоку
} else {
    int len  = length_base[sym - 257]  + read_bits(&bits, length_extra[sym - 257]);
    int dcode = decode_symbol(&bits, &dist_tree);
    int dist = dist_base[dcode] + read_bits(&bits, dist_extra[dcode]);
    for (int i = 0; i < len; i++) {            // копіюємо байт за байтом
        out[pos] = out[pos - dist];            // джерело може наздоганяти само себе
        pos++;
    }
}
