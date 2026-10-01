#ifndef CAMERA_PINS_H
#define CAMERA_PINS_H

// Розпіновка GPIO для плати AI-Thinker ESP32-CAM
#define CAM_PIN_PWDN    32  // Лінія живлення камери (Power Down)
#define CAM_PIN_RESET   -1  // Апаратне скидання відсутнє (-1)
#define CAM_PIN_XCLK     0  // Тактовий сигнал камери XCLK
#define CAM_PIN_SIOD    26  // Шина керування SCCB SDA
#define CAM_PIN_SIOC    27  // Шина керування SCCB SCL

#define CAM_PIN_D7      35  // Паралельна шина даних DVP (Y9)
#define CAM_PIN_D6      34  // Паралельна шина даних DVP (Y8)
#define CAM_PIN_D5      39  // Паралельна шина даних DVP (Y7)
#define CAM_PIN_D4      36  // Паралельна шина даних DVP (Y6)
#define CAM_PIN_D3      21  // Паралельна шина даних DVP (Y5)
#define CAM_PIN_D2      19  // Паралельна шина даних DVP (Y4)
#define CAM_PIN_D1      18  // Паралельна шина даних DVP (Y3)
#define CAM_PIN_D0       5  // Паралельна шина даних DVP (Y2)

#define CAM_PIN_VSYNC   25  // Кадрова синхронізація
#define CAM_PIN_HREF    23  // Рядкова синхронізація
#define CAM_PIN_PCLK    22  // Піксельне тактування

#endif // CAMERA_PINS_H
