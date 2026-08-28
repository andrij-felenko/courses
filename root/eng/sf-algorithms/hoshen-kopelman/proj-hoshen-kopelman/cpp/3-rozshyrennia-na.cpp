// Обробка 3D сусідів у сучасному C++
int process_3d_site_cpp(HoshenKopelmanDSU& dsu, int back_lbl, int top_lbl, int left_lbl) {
    int roots[3];
    int count = 0;

    if (back_lbl > 0) roots[count++] = dsu.find_root(back_lbl);
    if (top_lbl > 0)  roots[count++] = dsu.find_root(top_lbl);
    if (left_lbl > 0) roots[count++] = dsu.find_root(left_lbl);

    if (count == 0) {
        return dsu.make_cluster();
    }

    int primary_root = roots[0];
    for (int i = 1; i < count; ++i) {
        primary_root = dsu.union_roots(primary_root, roots[i]);
    }

    dsu.add_site_to_root(primary_root);
    return primary_root;
}
