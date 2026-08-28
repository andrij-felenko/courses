// нормовані команди від контролера
float roll = 0.20f, pitch = 0.0f, yaw = 0.0f, thr = 0.50f;

// рядки матриці квадрокоптера-X: {roll, pitch, yaw, thr}
static const float MIX[4][4] = {
    { -1, +1, +1, +1 },   // мотор 1
    { -1, -1, -1, +1 },   // мотор 2
    { +1, +1, -1, +1 },   // мотор 3
    { +1, -1, +1, +1 },   // мотор 4
};

float out[4];
for (int i = 0; i < 4; i++)
    out[i] = MIX[i][0]*roll + MIX[i][1]*pitch + MIX[i][2]*yaw + MIX[i][3]*thr;
