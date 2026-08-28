/* Обробка одного рядка ґратки мовою C */
void process_raster_row_c(
    const uint8_t* row,
    int width,
    int row_idx,
    int* prev_row,
    int* curr_row,
    int* labels,
    int* max_label
) {
    for (int c = 0; c < width; ++c) {
        if (!row[c]) {
            curr_row[c] = 0;
            continue;
        }

        int top = (row_idx > 0) ? prev_row[c] : 0;
        int left = (c > 0) ? curr_row[c - 1] : 0;

        if (top == 0 && left == 0) {
            /* Створюємо новий кластер */
            (*max_label)++;
            labels[*max_label] = -1; /* Розмір 1 */
            curr_row[c] = *max_label;
        } else if (top > 0 && left == 0) {
            int root = find_root_c(labels, top);
            labels[root]--;
            curr_row[c] = root;
        } else if (top == 0 && left > 0) {
            int root = find_root_c(labels, left);
            labels[root]--;
            curr_row[c] = root;
        } else {
            /* Колізія міток */
            int root_top = find_root_c(labels, top);
            int root_left = find_root_c(labels, left);

            if (root_top == root_left) {
                labels[root_top]--;
                curr_row[c] = root_top;
            } else {
                int merged = union_roots_c(labels, root_top, root_left);
                labels[merged]--;
                curr_row[c] = merged;
            }
        }
    }
}
