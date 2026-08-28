#include <stdint.h>
#include <stdbool.h>

/* Таблиця переходів скінченного автомата квадратурного сигналу */
static const int8_t encoder_table[16] = {
     0,  /* 00 -> 00: немає руху */
     1,  /* 00 -> 01: CW */
    -1,  /* 00 -> 10: CCW */
     0,  /* 00 -> 11: помилка / стрибок */
    -1,  /* 01 -> 00: CCW */
     0,  /* 01 -> 01: немає руху */
     0,  /* 01 -> 10: помилка / стрибок */
     1,  /* 01 -> 11: CW */
     1,  /* 10 -> 00: CW */
     0,  /* 10 -> 01: помилка / стрибок */
     0,  /* 10 -> 10: немає руху */
    -1,  /* 10 -> 11: CCW */
     0,  /* 11 -> 00: помилка / стрибок */
    -1,  /* 11 -> 01: CCW */
     1,  /* 11 -> 10: CW */
     0   /* 11 -> 11: немає руху */
};

typedef struct {
    uint8_t prev_state;   /* Попередній 2-бітний стан каналів (A << 1) | B */
    int8_t  sub_count;    /* Проміжний лічильник чверть-кроків (0..3) */
    int32_t position;     /* Позиція енкодера в повних кліках */
} encoder_t;

void encoder_init(encoder_t *enc, uint8_t initial_a, uint8_t initial_b) {
    enc->prev_state = ((initial_a & 1) << 1) | (initial_b & 1);
    enc->sub_count = 0;
    enc->position = 0;
}

/* Функція викликається в таймерному перериванні кожні 1 мс */
void encoder_update(encoder_t *enc, uint8_t raw_a, uint8_t raw_b) {
    uint8_t curr_state = ((raw_a & 1) << 1) | (raw_b & 1);
    uint8_t index = (enc->prev_state << 2) | curr_state;
    int8_t delta = encoder_table[index];

    enc->prev_state = curr_state;

    if (delta != 0) {
        enc->sub_count += delta;
        /* Для енкодера з 4 змінами коду на один тактильний клік (detent) */
        if (enc->sub_count >= 4) {
            enc->position++;
            enc->sub_count -= 4;
        } else if (enc->sub_count <= -4) {
            enc->position--;
            enc->sub_count += 4;
        }
    }
}
