#ifndef CAMERA_PINS_H
#define CAMERA_PINS_H

// Апаратне призначення виводів (GPIO) плати ESP32-CAM (AI-Thinker) для модуля OV2640

// Сигнали живлення та скидання
#define CAM_PIN_PWDN    32
#define CAM_PIN_RESET   -1  // Апаратне скидання не підключене до окремого GPIO

// Сигнали тактування
#define CAM_PIN_XCLK     0  // Зовнішній тактовий сигнал камери (XCLK)
#define CAM_PIN_PCLK    22  // Піксельна тактова частота (PCLK)

// Послідовна шина керування (SCCB / I2C)
#define CAM_PIN_SIOD    26  // Дані SCCB (SDA)
#define CAM_PIN_SIOC    27  // Тактування SCCB (SCL)

// 8-бітна паралельна шина даних (D0-D7)
#define CAM_PIN_D7      35
#define CAM_PIN_D6      34
#define CAM_PIN_D5      39
#define CAM_PIN_D4      36
#define CAM_PIN_D3      21
#define CAM_PIN_D2      19
#define CAM_PIN_D1      18
#define CAM_PIN_D0       5

// Сигнали синхронізації кадру та рядків
#define CAM_PIN_VSYNC   25  // Вертикальна синхронізація (початок кадру)
#define CAM_PIN_HREF    23  // Горизонтальна синхронізація (дійсні пікселі)

#endif // CAMERA_PINS_H
