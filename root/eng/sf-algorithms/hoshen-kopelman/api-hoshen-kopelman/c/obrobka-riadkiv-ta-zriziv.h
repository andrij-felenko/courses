/* Обробка одного рядка 2D ґратки */
hk_error_t hk_process_row(
    hk_context_t* ctx,
    const uint8_t* row_input,
    int* row_output_labels
);

/* Обробка одного 2D зрізу 3D ґратки */
hk_error_t hk_process_slice_3d(
    hk_context_t* ctx,
    const uint8_t* slice_input,
    int* slice_output_labels
);
