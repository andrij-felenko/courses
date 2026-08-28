#include <stdint.h>
#include <stdbool.h>

/* Результати декодування стану */
typedef enum {
    QUAD_DIR_NONE = 0,
    QUAD_DIR_CW   = 1,
    QUAD_DIR_CCW  = -1
} quad_direction_t;

/* Структура стану квадратурного декодера */
typedef struct {
    int64_t  position;          /* Накопичена абсолютна позиція в кроках */
    uint32_t error_count;       /* Лічильник недійсних діагональних переходів */
    uint8_t  prev_valid_state;  /* Попередній валідний 2-бітний стан (0..3) */
    uint8_t  history_a;         /* Зсувний регістр історії вибірок каналу A */
    uint8_t  history_b;         /* Зсувний регістр історії вибірок каналу B */
    uint8_t  stable_a;          /* Відфільтрований стабільний рівень A (0/1) */
    uint8_t  stable_b;          /* Відфільтрований стабільний рівень B (0/1) */
} quad_decoder_t;

/* 
 * Таблиця переходів (FSM LUT).
 * Індекс = (prev_state << 2) | curr_state
 * Значення: 0 (немає руху), 1 (CW, вперед), -1 (CCW, назад), 2 (помилка/недійсний перехід)
 */
static const int8_t QUAD_FSM_LUT[16] = {
    /* 00->00, 00->01, 00->10, 00->11 */
       0,       1,      -1,       2,
    /* 01->00, 01->01, 01->10, 01->11 */
      -1,       0,       2,       1,
    /* 10->00, 10->01, 10->10, 10->11 */
       1,       2,       0,      -1,
    /* 11->00, 11->01, 11->10, 11->11 */
       2,      -1,       1,       0
};

/**
 * @brief Ініціалізація структури квадратурного декодера
 */
void quad_decoder_init(quad_decoder_t *dec, bool initial_raw_a, bool initial_raw_b) {
    if (!dec) return;
    
    dec->position = 0;
    dec->error_count = 0;
    dec->stable_a = initial_raw_a ? 1 : 0;
    dec->stable_b = initial_raw_b ? 1 : 0;
    dec->history_a = dec->stable_a ? 0xFF : 0x00;
    dec->history_b = dec->stable_b ? 0xFF : 0x00;
    dec->prev_valid_state = (dec->stable_a << 1) | dec->stable_b;
}

/**
 * @brief Крок обробки вибірок (викликається періодично з ISR таймера або опитування)
 * @param dec Вказівник на екземпляр декодера
 * @param raw_a Миттєвий логічний рівень каналу A з піна GPIO
 * @param raw_b Миттєвий логічний рівень каналу B з піна GPIO
 * @return quad_direction_t Напрям здійсненого кроку (CW, CCW або NONE)
 */
quad_direction_t quad_decoder_process(quad_decoder_t *dec, bool raw_a, bool raw_b) {
    if (!dec) return QUAD_DIR_NONE;

    /* 1. Цифрова мажоритарна фільтрація брязкоту (Debounce) */
    dec->history_a = (dec->history_a << 1) | (raw_a ? 1 : 0);
    dec->history_b = (dec->history_b << 1) | (raw_b ? 1 : 0);

    /* Рівень вважається стабільним, якщо 3 останні вибірки однакові */
    if ((dec->history_a & 0x07) == 0x07) {
        dec->stable_a = 1;
    } else if ((dec->history_a & 0x07) == 0x00) {
        dec->stable_a = 0;
    }

    if ((dec->history_b & 0x07) == 0x07) {
        dec->stable_b = 1;
    } else if ((dec->history_b & 0x07) == 0x00) {
        dec->stable_b = 0;
    }

    /* 2. Формування поточного 2-бітного стану */
    uint8_t curr_state = (dec->stable_a << 1) | dec->stable_b;

    /* Якщо стан не змінився — рух відсутній */
    if (curr_state == dec->prev_valid_state) {
        return QUAD_DIR_NONE;
    }

    /* 3. Декодування переходу через 4-бітний індекс LUT */
    uint8_t lut_index = (dec->prev_valid_state << 2) | curr_state;
    int8_t step = QUAD_FSM_LUT[lut_index];

    if (step == 2) {
        /* Фіксація недійсного діагонального переходу (00 <-> 11 або 01 <-> 10) */
        dec->error_count++;
        /* При помилці не змінюємо позицію, але оновлюємо попередній стан */
        dec->prev_valid_state = curr_state;
        return QUAD_DIR_NONE;
    }

    /* 4. Валідний перехід: оновлення позиції та збереження стану */
    dec->position += step;
    dec->prev_valid_state = curr_state;

    return (step > 0) ? QUAD_DIR_CW : QUAD_DIR_CCW;
}

/**
 * @brief Отримання поточної позиції
 */
int64_t quad_decoder_get_position(const quad_decoder_t *dec) {
    return dec ? dec->position : 0;
}

/**
 * @brief Отримання кількості зафіксованих помилок
 */
uint32_t quad_decoder_get_errors(const quad_decoder_t *dec) {
    return dec ? dec->error_count : 0;
}

/**
 * @brief Скидання лічильника позиції в нуль
 */
void quad_decoder_reset_position(quad_decoder_t *dec) {
    if (dec) {
        dec->position = 0;
    }
}
