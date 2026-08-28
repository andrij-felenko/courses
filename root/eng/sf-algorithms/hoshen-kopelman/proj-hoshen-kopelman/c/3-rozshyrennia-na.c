/* Обробка 3D сусідів (Back, Top, Left) для сайту (z, y, x) */
static int process_3d_site(HKDisjointSet* dsu, int back_lbl, int top_lbl, int left_lbl) {
    int neighbors[3];
    int count = 0;

    if (back_lbl > 0) neighbors[count++] = dsu_find(dsu, back_lbl);
    if (top_lbl > 0)  neighbors[count++] = dsu_find(dsu, top_lbl);
    if (left_lbl > 0) neighbors[count++] = dsu_find(dsu, left_lbl);

    if (count == 0) {
        /* Новий 3D кластер */
        return dsu_make_cluster(dsu);
    }

    /* Усі сусіди належать одному чи різним кластерам: виконуємо послідовне злиття */
    int primary_root = neighbors[0];
    for (int i = 1; i < count; ++i) {
        primary_root = dsu_union(dsu, primary_root, neighbors[i]);
    }

    /* Додаємо поточний вузол до об'єднаного кореня */
    dsu->labels[primary_root]--;
    return primary_root;
}
