// Керування кроковим мотором через DRV8833 для Arduino
#include <Arduino.h>

const int IN1 = 2;
const int IN2 = 3;
const int IN3 = 4;
const int IN4 = 5;
const int SLEEP_PIN = 6;

// Таблиця станів для напівкрокового режиму (8 кроків)
const uint8_t HALF_STEP_TABLE[8][4] = {
    {HIGH, LOW,  LOW,  LOW},   // Крок 1: Phase A+
    {HIGH, LOW,  HIGH, LOW},   // Крок 2: Phase A+ & B+
    {LOW,  LOW,  HIGH, LOW},   // Крок 3: Phase B+
    {LOW,  HIGH, HIGH, LOW},   // Крок 4: Phase A- & B+
    {LOW,  HIGH, LOW,  LOW},   // Крок 5: Phase A-
    {LOW,  HIGH, LOW,  HIGH},  // Крок 6: Phase A- & B-
    {LOW,  LOW,  LOW,  HIGH},  // Крок 7: Phase B-
    {HIGH, LOW,  LOW,  HIGH}   // Крок 8: Phase A+ & B-
};

void setup() {
    pinMode(IN1, OUTPUT);
    pinMode(IN2, OUTPUT);
    pinMode(IN3, OUTPUT);
    pinMode(IN4, OUTPUT);
    pinMode(SLEEP_PIN, OUTPUT);
    
    // Пробудження драйвера DRV8833
    digitalWrite(SLEEP_PIN, HIGH);
}

void stepMotor(int steps, bool clockwise, unsigned int delayMs) {
    static int currentStep = 0;
    
    for (int i = 0; i < steps; i++) {
        if (clockwise) {
            currentStep = (currentStep + 1) % 8;
        } else {
            currentStep = (currentStep + 7) % 8;
        }
        
        digitalWrite(IN1, HALF_STEP_TABLE[currentStep][0]);
        digitalWrite(IN2, HALF_STEP_TABLE[currentStep][1]);
        digitalWrite(IN3, HALF_STEP_TABLE[currentStep][2]);
        digitalWrite(IN4, HALF_STEP_TABLE[currentStep][3]);
        
        delay(delayMs);
    }
}

void loop() {
    stepMotor(400, true, 5);  // 400 напівкроків за годинниковою стрілкою
    delay(1000);
    stepMotor(400, false, 5); // 400 напівкроків проти годинникової стрілки
    delay(1000);
}
