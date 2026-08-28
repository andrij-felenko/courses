void msckf_marginalize_oldest(MsckfFilter* filter) {
    if (filter->window_size == 0) return;
    
    int old_dim = filter->cov_dim;
    int new_dim = old_dim - POSE_STATE_DIM;
    int rm_offset = IMU_STATE_DIM; /* видалення першої пози вікна */
    
    /* Зсув матриці коваріацій: видалення рядків та стовпців [rm_offset ... rm_offset+5] */
    double* new_P = (double*)malloc(new_dim * new_dim * sizeof(double));
    
    int dst_r = 0;
    for (int src_r = 0; src_r < old_dim; ++src_r) {
        if (src_r >= rm_offset && src_r < rm_offset + POSE_STATE_DIM) continue;
        int dst_c = 0;
        for (int src_c = 0; src_c < old_dim; ++src_c) {
            if (src_c >= rm_offset && src_c < rm_offset + POSE_STATE_DIM) continue;
            new_P[dst_r * new_dim + dst_c] = filter->P[src_r * old_dim + src_c];
            dst_c++;
        }
        dst_r++;
    }
    
    memcpy(filter->P, new_P, new_dim * new_dim * sizeof(double));
    free(new_P);
    
    /* Зсув поз у масиві вікна */
    for (int i = 0; i < filter->window_size - 1; ++i) {
        filter->window[i] = filter->window[i + 1];
    }
    filter->window_size--;
    filter->cov_dim = new_dim;
}
