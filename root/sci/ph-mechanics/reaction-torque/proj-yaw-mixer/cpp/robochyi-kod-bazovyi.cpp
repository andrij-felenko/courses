// Один рядок матриці змішувача: внесок мотора в кожен канал.
typedef struct {
    float throttle;   // завжди +1: спільний газ
    float roll;       // ±1: лівий/правий бік рами
    float pitch;      // ±1: передній/задній бік рами
    float yaw;        // +1 для CCW-гвинта, −1 для CW-гвинта
} MixRow;

// X-рама, 4 мотори. Порядок m1..m4 — як у таблиці вище.
static const MixRow MIX[4] = {
    // throttle  roll  pitch  yaw
    {  +1.0f,  -1.0f,  +1.0f,  +1.0f },  // m1: зад-право,  CCW
    {  +1.0f,  -1.0f,  -1.0f,  -1.0f },  // m2: перед-право, CW
    {  +1.0f,  +1.0f,  +1.0f,  -1.0f },  // m3: зад-ліво,   CW
    {  +1.0f,  +1.0f,  -1.0f,  +1.0f },  // m4: перед-ліво,  CCW
};

// Вхід: команди від регулятора орієнтації, кожна вже масштабована в частку.
// throttle ∈ [0..1]; roll/pitch/yaw ∈ [−1..+1] (нуль = без моменту).
void mix_naive(float throttle, float roll, float pitch, float yaw,
               float motor[4])
{
    for (int i = 0; i < 4; ++i) {
        motor[i] = MIX[i].throttle * throttle
                 + MIX[i].roll     * roll
                 + MIX[i].pitch    * pitch
                 + MIX[i].yaw      * yaw;
    }
}
