// ── Фазовий такт: влягання ВБУДОВАНЕ, а не «сподіваємось на delay» ─────────
#define SETTLE_MS  6u    // > динаміки перетворювача: чекаємо влягання
#define MEAS_MS    3u    // скільки мс збирати усереднений вимір

typedef enum { PH_SETTLE, PH_MEASURE } phase_t;

static phase_t  phase      = PH_SETTLE;
static uint16_t ph_ms      = 0;
static int32_t  meas_acc_p = 0;   // акумулятор потужності за вікно виміру
static uint16_t meas_n     = 0;
