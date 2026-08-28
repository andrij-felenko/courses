bool msckf_triangulate_feature(const MsckfFilter* filter, const FeatureTrack* track, Vec3* out_pos) {
    if (track->obs_count < 2) return false;
    
    /* Складання системи A * p_G = b за алгоритмом прямого лінійного перетворення (DLT) */
    double A[3][3] = {{0}};
    double b[3] = {0};
    
    for (int i = 0; i < track->obs_count; ++i) {
        int p_idx = track->obs[i].pose_idx;
        Vec3 p_c = filter->window[p_idx].pos;
        double u = track->obs[i].u;
        double v = track->obs[i].v;
        
        /* Вектор напрямку променя в системі камери: d = [u, v, 1]ᵀ */
        /* Проєкційна матриця на площину, перпендикулярну до променя: I - d * dᵀ / |d|² */
        double norm2 = u*u + v*v + 1.0;
        double P_proj[3][3] = {
            { 1.0 - u*u/norm2,     -u*v/norm2,       -u/norm2 },
            {    -u*v/norm2,    1.0 - v*v/norm2,     -v/norm2 },
            {      -u/norm2,         -v/norm2,    1.0 - 1.0/norm2 }
        };
        
        for (int r = 0; r < 3; ++r) {
            for (int c = 0; c < 3; ++c) {
                A[r][c] += P_proj[r][c];
                b[r] += P_proj[r][c] * ((c == 0) ? p_c.x : (c == 1 ? p_c.y : p_c.z));
            }
        }
    }
    
    /* Наближене розв'язання 3x3 системи (метод Крамера) */
    double det = A[0][0]*(A[1][1]*A[2][2] - A[1][2]*A[2][1]) -
                 A[0][1]*(A[1][0]*A[2][2] - A[1][2]*A[2][0]) +
                 A[0][2]*(A[1][0]*A[2][1] - A[1][1]*A[2][0]);
                 
    if (fabs(det) < 1e-6) return false; // поганий паралакс
    
    out_pos->x = (b[0]*(A[1][1]*A[2][2] - A[1][2]*A[2][1]) -
                  A[0][1]*(b[1]*A[2][2] - A[1][2]*b[2]) +
                  A[0][2]*(b[1]*A[2][1] - A[1][1]*b[2])) / det;
                  
    out_pos->y = (A[0][0]*(b[1]*A[2][2] - A[1][2]*b[2]) -
                  b[0]*(A[1][0]*A[2][2] - A[1][2]*A[2][0]) +
                  A[0][2]*(A[1][0]*b[2] - b[1]*A[2][0])) / det;
                  
    out_pos->z = (A[0][0]*(A[1][1]*b[2] - b[1]*A[2][1]) -
                  A[0][1]*(A[1][0]*b[2] - b[1]*A[2][0]) +
                  b[0]*(A[1][0]*A[2][1] - A[1][1]*A[2][0])) / det;
                  
    return true;
}
