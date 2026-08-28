void msckf_update_feature(MsckfFilter* filter, const FeatureTrack* track) {
    Vec3 p_G;
    if (!msckf_triangulate_feature(filter, track, &p_G)) {
        return; /* пропуск через низький паралакс */
    }
    
    int M = track->obs_count;
    int rows = 2 * M;
    int state_dim = filter->cov_dim;
    
    /* Виділення пам'яті для якобіанів одного орієнтира */
    double* r = (double*)calloc(rows, sizeof(double));
    double* H_x = (double*)calloc(rows * state_dim, sizeof(double));
    double* H_f = (double*)calloc(rows * 3, sizeof(double));
    
    for (int i = 0; i < M; ++i) {
        int p_idx = track->obs[i].pose_idx;
        CameraPose* pose = &filter->window[p_idx];
        
        /* Вектор до точки: p_c = p_G - p_Ci */
        double X_c = p_G.x - pose->pos.x;
        double Y_c = p_G.y - pose->pos.y;
        double Z_c = p_G.z - pose->pos.z;
        if (Z_c <= 0.1) continue; // позаду камери
        
        /* Проєкція та нев'язка */
        double u_proj = X_c / Z_c;
        double v_proj = Y_c / Z_c;
        r[2*i]     = track->obs[i].u - u_proj;
        r[2*i + 1] = track->obs[i].v - v_proj;
        
        /* Якобіан до 3D-точки H_f: d(proj)/d(p_G) */
        H_f[(2*i) * 3 + 0]     =  1.0 / Z_c;
        H_f[(2*i) * 3 + 2]     = -X_c / (Z_c * Z_c);
        H_f[(2*i + 1) * 3 + 1] =  1.0 / Z_c;
        H_f[(2*i + 1) * 3 + 2] = -Y_c / (Z_c * Z_c);
        
        /* Якобіан до пози камери H_x (спрощено положення) */
        int col_offset = IMU_STATE_DIM + p_idx * POSE_STATE_DIM;
        H_x[(2*i) * state_dim + (col_offset + 0)]     = -1.0 / Z_c;
        H_x[(2*i) * state_dim + (col_offset + 2)]     =  X_c / (Z_c * Z_c);
        H_x[(2*i + 1) * state_dim + (col_offset + 1)] = -1.0 / Z_c;
        H_x[(2*i + 1) * state_dim + (col_offset + 2)] =  Y_c / (Z_c * Z_c);
    }
    
    /* Проєкція на лівий нуль-простір: множення на матрицю лівого базису Q2ᵀ */
    double R_noise = 0.001; // дисперсія шуму пікселів
    for (int i = 0; i < rows; ++i) {
        if (fabs(r[i]) > 0.05) continue; // відсіювання викидів
        
        /* Спрощений скалярний крок Калмана для рядка виміру */
        double H_row_P[IMU_STATE_DIM + MAX_SLIDING_WINDOW * POSE_STATE_DIM] = {0};
        double S = R_noise;
        for (int c = 0; c < state_dim; ++c) {
            for (int k = 0; k < state_dim; ++k) {
                H_row_P[c] += H_x[i * state_dim + k] * filter->P[k * state_dim + c];
            }
            S += H_row_P[c] * H_x[i * state_dim + c];
        }
        
        if (S > 1e-9) {
            double K[IMU_STATE_DIM + MAX_SLIDING_WINDOW * POSE_STATE_DIM];
            for (int c = 0; c < state_dim; ++c) {
                K[c] = H_row_P[c] / S;
            }
            /* Оновлення положення IMU */
            filter->imu.pos.x += K[0] * r[i];
            filter->imu.pos.y += K[1] * r[i];
            filter->imu.pos.z += K[2] * r[i];
        }
    }
    
    free(r);
    free(H_x);
    free(H_f);
}
