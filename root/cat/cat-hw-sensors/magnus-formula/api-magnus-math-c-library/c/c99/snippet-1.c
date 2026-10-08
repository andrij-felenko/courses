#include <stdint.h>

// Структура емпіричних коефіцієнтів формули Магнуса
typedef struct {
    float a; // Основний масштабний коефіцієнт [hPa]
    float b; // Безрозмірний температурний коефіцієнт
    float c; // Температурний зсув знаменника [°C]
} magnus_params_t;

// Набори коефіцієнтів для різних фазових станів і температур
static const magnus_params_t MAGNUS_PARAMS_WATER = {
    .a = 6.112f,
    .b = 17.62f,
    .c = 243.12f
};

static const magnus_params_t MAGNUS_PARAMS_ICE = {
    .a = 6.112f,
    .b = 22.46f,
    .c = 272.62f
};

static const magnus_params_t MAGNUS_PARAMS_HIGH_TEMP = {
    .a = 6.112f,
    .b = 18.729f,
    .c = 257.87f
};
