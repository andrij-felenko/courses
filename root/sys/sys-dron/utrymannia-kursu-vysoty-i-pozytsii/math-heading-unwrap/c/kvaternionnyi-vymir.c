typedef struct { float w, x, y, z; } Quaternion;

void quat_shortest_arc(Quaternion *q_err) {
    if (q_err->w < 0.0f) {
        q_err->w = -q_err->w;
        q_err->x = -q_err->x;
        q_err->y = -q_err->y;
        q_err->z = -q_err->z;
    }
}
