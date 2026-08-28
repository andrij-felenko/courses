// Ідіоматична реалізація мовою C++20 з використанням std::span
void process_raster_row_cpp(
    std::span<const uint8_t> row,
    int row_idx,
    std::span<const int> prev_row,
    std::span<int> curr_row,
    HoshenKopelmanDSU& dsu
) {
    const int width = static_cast<int>(row.size());

    for (int c = 0; c < width; ++c) {
        if (!row[c]) {
            curr_row[c] = 0;
            continue;
        }

        int top = (row_idx > 0) ? prev_row[c] : 0;
        int left = (c > 0) ? curr_row[c - 1] : 0;

        if (top == 0 && left == 0) {
            curr_row[c] = dsu.make_cluster();
        } else if (top > 0 && left == 0) {
            int root = dsu.find_root(top);
            dsu.add_site_to_root(root);
            curr_row[c] = root;
        } else if (top == 0 && left > 0) {
            int root = dsu.find_root(left);
            dsu.add_site_to_root(root);
            curr_row[c] = root;
        } else {
            int root_top = dsu.find_root(top);
            int root_left = dsu.find_root(left);

            if (root_top == root_left) {
                dsu.add_site_to_root(root_top);
                curr_row[c] = root_top;
            } else {
                int merged = dsu.union_roots(root_top, root_left);
                dsu.add_site_to_root(merged);
                curr_row[c] = merged;
            }
        }
    }
}
