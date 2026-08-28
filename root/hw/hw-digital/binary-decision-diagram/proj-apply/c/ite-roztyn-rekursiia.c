static int ite(int f, int g, int h) {
    if (f == BDD_TRUE)  return g;                /* ITE(1,g,h) = g */
    if (f == BDD_FALSE) return h;                /* ITE(0,g,h) = h */
    if (g == h)         return g;                /* обидві гілки однакові */
    if (g == BDD_TRUE && h == BDD_FALSE) return f;   /* ITE(f,1,0) = f */

    unsigned slot = hash3(f, g, h) & cmask;      /* кеш: чи рахували цю трійку? */
    Cache *e = &ctable[slot];
    if (e->f == f && e->g == g && e->h == h) return e->r;

    int v = nodes[f].var;                        /* верхня змінна серед f, g, h */
    if (nodes[g].var < v) v = nodes[g].var;
    if (nodes[h].var < v) v = nodes[h].var;

    #define COF(u, br) (nodes[u].var == v ? nodes[u].br : (u))   /* кофактор за v */
    int lo = ite(COF(f, lo), COF(g, lo), COF(h, lo));           /* гілка v = 0 */
    int hi = ite(COF(f, hi), COF(g, hi), COF(h, hi));           /* гілка v = 1 */
    #undef COF

    int r = make_node(v, lo, hi);                /* збірка — знову з обома скороченнями */
    e->f = f; e->g = g; e->h = h; e->r = r;      /* кешуємо (слот перезаписуємо — кеш втратний) */
    return r;
}
