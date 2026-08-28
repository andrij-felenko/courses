#include "main.h"   // CubeMX згенерував IN1_GPIO_Port / IN1_Pin і решту

// Виводи задано в CubeMX: GPIO_Output, Push-Pull, No pull, Low speed.
// Такт порту вмикає й режим виставляє MX_GPIO_Init() — окремої ініціалізації нема.

// Вісім станів half-step. Рядок — один такт; стовпці — IN1..IN4.
// 1 = обмотку під струмом (вхід у 1), 0 = знеструмлено.
static const uint8_t seq[8][4] = {
  {1, 0, 0, 0},   // крок 1
  {1, 1, 0, 0},   // крок 2
  {0, 1, 0, 0},   // крок 3
  {0, 1, 1, 0},   // крок 4
  {0, 0, 1, 0},   // крок 5
  {0, 0, 1, 1},   // крок 6
  {0, 0, 0, 1},   // крок 7
  {1, 0, 0, 1},   // крок 8
};

// Порт і пін лежать нарізно, тож складемо їх поруч — ходитимемо циклом
static GPIO_TypeDef *const PORTS[4] = { IN1_GPIO_Port, IN2_GPIO_Port,
                                        IN3_GPIO_Port, IN4_GPIO_Port };
static const uint16_t      PINS[4]  = { IN1_Pin, IN2_Pin, IN3_Pin, IN4_Pin };
