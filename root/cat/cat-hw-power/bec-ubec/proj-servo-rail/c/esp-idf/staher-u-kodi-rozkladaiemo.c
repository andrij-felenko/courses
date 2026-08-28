// ── Неблокувальний стагер на ESP-IDF. Той самий принцип. ──
// Розклад пусків + монотонний esp_timer; команди йдуть по черзі,
// задача не блокується — між пусками крутиться решта роботи.
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"

#define N 4
#define STAGGER_MS 90                  // крок між пусками серв, мс

static uint8_t target[N];              // куди кожне серво має піти, градуси
static int64_t due_at[N];              // момент (мс), коли дозволено рушити
static bool    pending[N];             // чи чекає це серво своєї черги

static int64_t now_ms(void) { return esp_timer_get_time() / 1000; }

// Задати нову «розкладку» цілей: серва рушать по черзі, а не разом.
void schedule_move(const uint8_t deg[N]) {
    int64_t now = now_ms();
    for (int i = 0; i < N; i++) {
        target[i]  = deg[i];
        due_at[i]  = now + (int64_t)i * STAGGER_MS;   // i-те чекає i кроків
        pending[i] = true;
    }
}

// Викликати ЧАСТО: видає команди, коли настав їхній час.
void service_stagger(void) {
    int64_t now = now_ms();
    for (int i = 0; i < N; i++) {
        if (pending[i] && now - due_at[i] >= 0) {
            servo_write(i, target[i]);            // рушаємо ОДНЕ
            pending[i] = false;
        }
    }
}

void servo_task(void *arg) {
    servo_init();                                 // усі серва — у центр
    int64_t last = 0;
    for (;;) {
        if (now_ms() - last > 3000) {   // раз на 3 с нові кути — по черзі
            const uint8_t goal[N] = {30, 60, 120, 150};
            schedule_move(goal);
            last = now_ms();
        }
        service_stagger();      // піки рознесені; тут-таки радіо, вимір шини…
        vTaskDelay(pdMS_TO_TICKS(5));
    }
}
