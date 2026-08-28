#include <Wire.h>
#include <MPU6050_6Axis_MotionApps20.h>   // варіант бібліотеки З підтримкою DMP

MPU6050 mpu;

uint8_t  fifoBuffer[64];   // сюди читаємо один пакет FIFO
uint16_t packetSize;       // розмір пакета DMP — дізнаємось у чипа
Quaternion q;              // кватерніон [w, x, y, z]
VectorFloat gravity;       // напрям тяжіння, відновлений із кватерніона
float ypr[3];              // yaw, pitch, roll — у РАДІАНАХ

void setup() {
    Serial.begin(115200);
    Wire.begin();
    Wire.setClock(400000);     // DMP любить швидку шину (400 кГц)

    mpu.initialize();
    if (!mpu.testConnection()) { Serial.println(F("немає чипа")); while (1); }

    // Заливаємо образ DMP у чип. Повертає 0, якщо все гаразд.
    uint8_t status = mpu.dmpInitialize();

    // Зсуви нуля — конкретні для КОЖНОГО екземпляра (див. розділ про калібрування).
    // Ці числа беруться з калібрувального прогону; тут — приклад.
    mpu.setXGyroOffset(220);
    mpu.setYGyroOffset(76);
    mpu.setZGyroOffset(-85);
    mpu.setZAccelOffset(1788);

    if (status == 0) {
        // Автоматичне тонке калібрування нуля (6 ітерацій — компроміс точність/час).
        mpu.CalibrateAccel(6);
        mpu.CalibrateGyro(6);
        mpu.setDMPEnabled(true);           // з цієї миті DMP сам пише у FIFO
        packetSize = mpu.dmpGetFIFOPacketSize();   // дізнаємось розмір пакета
        Serial.println(F("DMP готовий"));
    } else {
        // status 1 — не завантажилась память, 2 — не запустились налаштування DMP
        Serial.print(F("DMP не стартував, код ")); Serial.println(status);
        while (1);
    }
}

void loop() {
    // Тягнемо найсвіжіший цілий пакет із FIFO. Повертає true, якщо пакет є.
    // Ця функція сама впорається з переповненням FIFO (див. пастку нижче).
    if (mpu.dmpGetCurrentFIFOPacket(fifoBuffer)) {
        mpu.dmpGetQuaternion(&q, fifoBuffer);      // байти → кватерніон
        mpu.dmpGetGravity(&gravity, &q);           // кватерніон → напрям низу
        mpu.dmpGetYawPitchRoll(ypr, &q, &gravity); // → yaw/pitch/roll (радіани)

        // Переводимо в градуси: 180/π радіан у градусі.
        float yaw   = ypr[0] * 180.0f / M_PI;
        float pitch = ypr[1] * 180.0f / M_PI;
        float roll  = ypr[2] * 180.0f / M_PI;

        Serial.print(F("yaw "));   Serial.print(yaw, 1);
        Serial.print(F("  pitch ")); Serial.print(pitch, 1);
        Serial.print(F("  roll "));  Serial.println(roll, 1);
    }
}
