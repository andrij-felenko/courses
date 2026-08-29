#ifndef FM_REPORT_H
#define FM_REPORT_H

#include <stdint.h>

/* Значення з чинного набору MAVLink — саме вони йдуть у пакетах, тож підміняти
   їх «своїми зручними» не можна: наземна станція розбирає числа, не назви. */
#define MAV_CMD_DO_SET_MODE            176u

#define MAV_RESULT_ACCEPTED              0u
#define MAV_RESULT_TEMPORARILY_REJECTED  1u
#define MAV_RESULT_DENIED                2u
#define MAV_RESULT_UNSUPPORTED           3u
#define MAV_RESULT_FAILED                4u

#define MAV_SEVERITY_EMERGENCY 0u
#define MAV_SEVERITY_ALERT     1u
#define MAV_SEVERITY_CRITICAL  2u
#define MAV_SEVERITY_ERROR     3u
#define MAV_SEVERITY_WARNING   4u
#define MAV_SEVERITY_NOTICE    5u
#define MAV_SEVERITY_INFO      6u

/* Поле text пакета STATUSTEXT — рівно 50 байтів без завершального нуля.
   Довший рядок станція обрізає мовчки, тож ріжемо його самі й свідомо. */
#define FM_STATUSTEXT_LEN 50

/* Сигнали зумера: пілот у полі чує їх швидше, ніж читає екран станції. */
typedef enum {
    FM_TONE_NONE = 0,
    FM_TONE_MODE_ACCEPTED,
    FM_TONE_MODE_REJECTED,   /* охоронець не пустив                            */
    FM_TONE_THROTTLE_LOCK,   /* стік газу не зведено з авторегулятором         */
    FM_TONE_FAILSAFE,        /* витіснення аварійним режимом                   */
    FM_TONE_DISARM
} fm_tone_t;

/* Вихідний канал автомата. Автомат нічого не знає ні про UART, ні про буфери
   телеметрії: він викликає ці функції, а їх підставляє носій — прошивка,
   стенд або тест. Порожні вказівники дозволені: автомат мовчить, а не падає. */
typedef struct {
    void (*command_ack)(void *ctx, uint16_t command, uint8_t result);
    void (*statustext)(void *ctx, uint8_t severity, const char *text);
    void (*tone)(void *ctx, fm_tone_t tone);
    void *ctx;
} fm_reporter_t;

void fm_report_ack(const fm_reporter_t *r, uint16_t command, uint8_t result);
void fm_report_text(const fm_reporter_t *r, uint8_t severity, const char *text);
void fm_report_tone(const fm_reporter_t *r, fm_tone_t tone);

#endif /* FM_REPORT_H */
