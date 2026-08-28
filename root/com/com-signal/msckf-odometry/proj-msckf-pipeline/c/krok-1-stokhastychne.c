void msckf_augment_state(MsckfFilter* filter, double timestamp, Vec3 p_bc, Quat q_bc) {
    if (filter->window_size >= MAX_SLIDING_WINDOW) {
        return;
    }
    
    int n = filter->window_size;
    int old_dim = IMU_STATE_DIM + n * POSE_STATE_DIM;
    int new_dim = old_dim + POSE_STATE_DIM;
    
    /* 1. Обчислення пози камери: p_C = p_I + R_I * p_BC */
    CameraPose* new_pose = &filter->window[n];
    new_pose->timestamp = timestamp;
    new_pose->pos.x = filter->imu.pos.x + p_bc.x;
    new_pose->pos.y = filter->imu.pos.y + p_bc.y;
    new_pose->pos.z = filter->imu.pos.z + p_bc.z;
    new_pose->att = filter->imu.att; /* спрощено для екстринсиків */
    
    /* 2. Розширення матриці коваріацій P */
    /* Копіювання кореляції IMU -> Нова поза (J_clone = I) */
    for (int r = 0; r < old_dim; ++r) {
        for (int c = 0; c < POSE_STATE_DIM; ++c) {
            double cov_val = filter->P[r * old_dim + c];
            filter->P[r * new_dim + (old_dim + c)] = cov_val;
            filter->P[(old_dim + c) * new_dim + r] = cov_val;
        }
    }
    
    /* Нижній правий блок нової пози */
    for (int r = 0; r < POSE_STATE_DIM; ++r) {
        for (int c = 0; c < POSE_STATE_DIM; ++c) {
            filter->P[(old_dim + r) * new_dim + (old_dim + c)] = filter->P[r * old_dim + c];
        }
    }
    
    filter->window_size++;
    filter->cov_dim = new_dim;
}
