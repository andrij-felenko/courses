#include <Wire.h>
#include <VL53L0X.h>

const uint8_t SENSOR_COUNT = 2;
const uint8_t XSHUT_PINS[SENSOR_COUNT] = {4, 5};
const uint8_t INTERRUPT_PINS[SENSOR_COUNT] = {2, 3};
const uint8_t NEW_ADDRESSES[SENSOR_COUNT] = {0x30, 0x31};

VL53L0X sensors[SENSOR_COUNT];
volatile bool dataReady[SENSOR_COUNT] = {false, false};

void IRAM_ATTR onSensor0Interrupt() { dataReady[0] = true; }
void IRAM_ATTR onSensor1Interrupt() { dataReady[1] = true; }

void setup() {
  Serial.begin(115200);
  Wire.begin();

  // Крок 1: Переведення всіх чипів у режим сну
  for (uint8_t i = 0; i < SENSOR_COUNT; i++) {
    pinMode(XSHUT_PINS[i], OUTPUT);
    digitalWrite(XSHUT_PINS[i], LOW);
  }
  delay(10);

  // Крок 2: Послідовна активація та зміна адрес
  for (uint8_t i = 0; i < SENSOR_COUNT; i++) {
    digitalWrite(XSHUT_PINS[i], HIGH);
    delay(10);
    
    sensors[i].setAddress(NEW_ADDRESSES[i]);
    sensors[i].init();
    sensors[i].setTimeout(500);
    sensors[i].startContinuous();
  }

  // Крок 3: Налаштування апаратних переривань
  pinMode(INTERRUPT_PINS[0], INPUT_PULLUP);
  pinMode(INTERRUPT_PINS[1], INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(INTERRUPT_PINS[0]), onSensor0Interrupt, FALLING);
  attachInterrupt(digitalPinToInterrupt(INTERRUPT_PINS[1]), onSensor1Interrupt, FALLING);
}

void loop() {
  for (uint8_t i = 0; i < SENSOR_COUNT; i++) {
    if (dataReady[i]) {
      dataReady[i] = false;
      uint16_t distance = sensors[i].readRangeContinuousMillimeters();
      Serial.print("Сенсор ");
      Serial.print(i);
      Serial.print(": ");
      Serial.print(distance);
      Serial.println(" мм");
    }
  }
}
