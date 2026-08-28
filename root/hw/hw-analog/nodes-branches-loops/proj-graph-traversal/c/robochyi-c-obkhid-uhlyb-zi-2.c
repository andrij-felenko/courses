/* зібрати фундаментальний контур хорди br у out[]; повернути к-ть гілок */
static uint8_t collect_loop(uint8_t br, Branch *branches, uint8_t *out) {
    uint8_t a = branches[br].a, b = branches[br].b;
    uint8_t len = 0;
    out[len++] = br;                             /* сама хорда замикає контур   */

    /* глибина кожного кінця від кореня дерева */
    uint8_t da = 0, db = 0;
    for (int8_t x = a; x != -1; x = parent_node[x]) da++;
    for (int8_t x = b; x != -1; x = parent_node[x]) db++;

    int8_t pa = a, pb = b;
    /* підняти глибший кінець до рівня — і зібрати пройдені ним гілки */
    while (da > db) { out[len++] = parent_br[pa]; pa = parent_node[pa]; da--; }
    while (db > da) { out[len++] = parent_br[pb]; pb = parent_node[pb]; db--; }
    /* далі крокуємо разом до спільного предка, збираючи гілки з обох боків */
    while (pa != pb) {
        out[len++] = parent_br[pa]; pa = parent_node[pa];
        out[len++] = parent_br[pb]; pb = parent_node[pb];
    }
    return len;                                  /* out[0..len) — гілки контуру */
}
