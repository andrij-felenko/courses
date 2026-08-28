const float V_SETPOINT = 1.05f;  // напруга бажаного проміжку (~30 см за таблицею)
const float KP         = 200.0f; // коефіцієнт П-регулятора

void loopHoldGap() {
    float v     = readSensorVolts(SENSOR_PIN);
    float err   = v - V_SETPOINT;     // v більша → ціль ближча, ніж треба
    int   drive = int(-KP * err);     // ближча → їхати назад
    drive = constrain(drive, -255, 255);
    setMotor(drive);                  // ваш драйвер мотора
    delay(20);
}
