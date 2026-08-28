// Розводка сенсора OV2640 на платі AI-Thinker ESP32-CAM.
// Ці номери НЕ вигадують — вони визначені розводкою плати.
#define PWDN_GPIO_NUM  32   // power-down сенсора
#define RESET_GPIO_NUM -1   // апаратного reset немає (−1 = не використовується)
#define XCLK_GPIO_NUM   0   // тактовий сигнал для сенсора
#define SIOD_GPIO_NUM  26   // SCCB data (керування сенсором, як I2C)
#define SIOC_GPIO_NUM  27   // SCCB clock
#define Y9_GPIO_NUM    35   // D7  ─┐
#define Y8_GPIO_NUM    34   // D6   │
#define Y7_GPIO_NUM    39   // D5   │
#define Y6_GPIO_NUM    36   // D4   │ вісім ліній даних
#define Y5_GPIO_NUM    21   // D3   │ паралельного порту DVP
#define Y4_GPIO_NUM    19   // D2   │
#define Y3_GPIO_NUM    18   // D1   │
#define Y2_GPIO_NUM     5   // D0  ─┘
#define VSYNC_GPIO_NUM 25   // синхронізація кадру
#define HREF_GPIO_NUM  23   // синхронізація рядка
#define PCLK_GPIO_NUM  22   // тактовий сигнал пікселів
