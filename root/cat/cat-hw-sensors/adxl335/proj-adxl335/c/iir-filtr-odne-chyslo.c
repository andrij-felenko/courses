Iir fx, fy, fz;                 // по фільтру на вісь
const float A = 0.15f;          // золота середина: помітно тихіше, ще не мляво

void loop() {
    float ax = iirStep(&fx, readG(A0, 0), A);
    float ay = iirStep(&fy, readG(A1, 1), A);
    float az = iirStep(&fz, readG(A2, 2), A);   // Z шумніша вдвічі — фільтр тут особливо доречний

    float pitch, roll;
    tiltAngles(ax, ay, az, &pitch, &roll);
    Serial.print(pitch, 1); Serial.print('\t'); Serial.println(roll, 1);
    delay(20);
}
