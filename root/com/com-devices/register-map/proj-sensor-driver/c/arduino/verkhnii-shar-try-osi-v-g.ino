void setup() {
    Wire.begin();
    if (!mpu_present()) { /* біда з дротами/адресою */ return; }
    if (mpu_begin() != MPU_OK) { /* збій налаштування */ return; }
}

void loop() {
    float ax, ay, az;
    if (mpu_read_accel(&ax, &ay, &az) == MPU_OK) {
        // ax, ay, az — у g, можна використовувати
    }
}
