#include "board.h"
#include "pipeline.h"

#include "stm32g0xx.h"

/* Уставка: тримаємо на вході 1650 мВ, тобто половину опори. */
#define SETPOINT_MV 1650U

/* Коефіцієнти у Q8.8. Порахувати їх у мові препроцесора можна ще під час
   збирання — у прошивку поїдуть готові цілі, жодного float у коді. */
#define KP_Q8 ((int32_t)(2.5 * Q8_ONE))  /* 640  */
#define KI_Q8 ((int32_t)(0.1 * Q8_ONE))  /* 25   */
#define KD_Q8 ((int32_t)(1.2 * Q8_ONE))  /* 307  */

/* Уся пам'ять конвеєра — одна статична структура. Ні malloc, ні new:
   фрагментації купи в контурі реального часу просто немає звідки взятися. */
static pipeline_t s_pipeline;

/* Прапорець для фонового циклу. Пише його переривання, читає main,
   тож volatile обов'язковий. */
static volatile uint32_t s_ticks;

/* Гачок із board.c: викликається кожні 10 мс із переривання DMA.
   Тут не має бути нічого, крім самого конвеєра: увесь прохід — близько
   сімдесяти тактів, і саме тому джитера періоду немає. */
void app_on_sample(uint16_t raw_adc)
{
    const uint16_t duty = pipeline_step(&s_pipeline, raw_adc, SETPOINT_MV);
    board_set_duty(duty);
    ++s_ticks;
}

int main(void)
{
    const pid_cfg_t pid_cfg = {
        .kp_q8 = KP_Q8,
        .ki_q8 = KI_Q8,
        .kd_q8 = KD_Q8,
        .out_min = 0,
        .out_max = PWM_MAX_DUTY,
    };

    /* alpha = 1/8: зсув на три розряди, один такт процесора. */
    if (!pipeline_init(&s_pipeline, 3U, &pid_cfg)) {
        board_panic(BOARD_ERR_BAD_CONFIG); /* коефіцієнти не пройшли перевірку меж */
    }

    const board_status_t status = board_init();
    if (status != BOARD_OK) {
        board_panic(status);
    }

    for (;;) {
        /* Регулювання цілком живе в перериванні. Фоновому циклу лишається
           зв'язок, журнал, сторожовий таймер — тут просто спимо до
           наступного переривання, і 99.98% часу ядро не витрачає струм. */
        __WFI();
    }
}
