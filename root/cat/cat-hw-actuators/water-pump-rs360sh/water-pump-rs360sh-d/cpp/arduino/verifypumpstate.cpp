const int PUMP_PWM_PIN = 9;
const int CURRENT_SENSOR_PIN = A0;

const int DRY_RUN_THRESHOLD = 150;  // Analog threshold for dry run detection
const int OVERCURRENT_THRESHOLD = 800; // Analog threshold for motor stall
const unsigned long STARTUP_GRACE_MS = 300; // Startup surge delay

enum PumpStatus {
  PUMP_NORMAL,
  ERROR_DRY_RUN,
  ERROR_OVERCURRENT
};

PumpStatus verifyPumpState(unsigned long activeTimeMs) {
  int sensorValue = analogRead(CURRENT_SENSOR_PIN);

  // Skip checks during soft-start motor inrush phase
  if (activeTimeMs < STARTUP_GRACE_MS) {
    return PUMP_NORMAL;
  }

  if (sensorValue < DRY_RUN_THRESHOLD) {
    return ERROR_DRY_RUN;
  } else if (sensorValue > OVERCURRENT_THRESHOLD) {
    return ERROR_OVERCURRENT;
  }

  return PUMP_NORMAL;
}
