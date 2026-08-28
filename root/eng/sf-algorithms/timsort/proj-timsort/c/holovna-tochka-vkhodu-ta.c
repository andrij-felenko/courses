void timsort(int *arr, size_t n) {
    if (n < 2) return;

    size_t minrun = calculate_minrun(n);
    TimSortState state;
    state.array = arr;
    state.size = n;
    state.temp_buf = NULL;
    state.temp_capacity = 0;
    state.min_gallop = MIN_GALLOP_DEFAULT;
    state.stack_size = 0;

    size_t start = 0;
    while (start < n) {
        size_t run_len = count_and_reverse_run(arr, start, n);

        if (run_len < minrun) {
            size_t force = (n - start < minrun) ? (n - start) : minrun;
            binary_insertion_sort(arr, start, force, run_len);
            run_len = force;
        }

        state.stack[state.stack_size].start = start;
        state.stack[state.stack_size].len = run_len;
        state.stack_size++;

        merge_collapse(&state);
        start += run_len;
    }

    merge_force_collapse(&state);

    if (state.temp_buf) {
        free(state.temp_buf);
    }
}

int main(void) {
    int test_data[] = { 42, 17, 93, 8, 12, 65, 88, 5, 23, 71, 3, 50, 81, 19, 34, 99 };
    size_t n = sizeof(test_data) / sizeof(test_data[0]);

    printf("Початковий масив:\n");
    for (size_t i = 0; i < n; i++) printf("%d ", test_data[i]);
    printf("\n");

    timsort(test_data, n);

    printf("Відсортований масив:\n");
    for (size_t i = 0; i < n; i++) printf("%d ", test_data[i]);
    printf("\n");

    for (size_t i = 1; i < n; i++) {
        if (test_data[i] < test_data[i - 1]) {
            printf("ПОМИЛКА СОРТУВАННЯ!\n");
            return 1;
        }
    }
    printf("Сортування успішно підтверджено!\n");
    return 0;
}
