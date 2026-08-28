/* Єдине місце, де народжується вузол. Повертає КАНОНІЧНИЙ вузол (var, lo, hi):
   якщо такий уже є — наявний, інакше створює новий. */
static int make_node(int var, int lo, int hi) {
    if (lo == hi) return lo;                     /* скорочення 1: гілки збіглися — питання зайве */

    unsigned slot = hash3(var, lo, hi) & umask;  /* скорочення 2: шукаємо двійника в кошику */
    for (int u = utable[slot]; u != -1; u = nodes[u].next)
        if (nodes[u].var == var && nodes[u].lo == lo && nodes[u].hi == hi)
            return u;                             /* уже існує — віддаємо той самий вузол */

    if (nnodes == ncap) { ncap *= 2; nodes = realloc(nodes, sizeof(Node) * ncap); }
    int u = nnodes++;                             /* новий канонічний вузол */
    nodes[u] = (Node){ var, lo, hi, utable[slot], 0 };
    utable[slot] = u;                             /* чіпляємо в голову ланцюжка кошика */
    nodes[lo].ref++; nodes[hi].ref++;             /* тримаємо нащадків живими */
    return u;
}
