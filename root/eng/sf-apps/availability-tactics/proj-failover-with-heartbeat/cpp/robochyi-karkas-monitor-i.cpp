#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

// Скільки часу між ударами й скільки пропусків терпимо — це НЕ константи
// «з голови», а прямий переклад сценарію доступності в числа:
//   BEAT_PERIOD_MS  — як часто головний зобов'язаний битися;
//   MISS_LIMIT      — скільки ударів підряд може пропасти, поки ми ще
//                     не оголошуємо смерть (це і є ГІСТЕРЕЗИС виявлення).
#define BEAT_PERIOD_MS   500u
#define MISS_LIMIT       3u        // смерть визнаємо після ~1.5 с тиші

typedef enum { NODE_UP, NODE_SUSPECT, NODE_DOWN } health_t;

typedef struct {
    uint32_t last_beat_ms;   // час останнього почутого удару
    uint32_t missed;         // скільки періодів поспіль тиша
    health_t health;         // поточний присуд монітора
} NodeHealth;

void health_init(NodeHealth *h, uint32_t now_ms) {
    h->last_beat_ms = now_ms;
    h->missed = 0;
    h->health = NODE_UP;
}

// Прийшов фізичний удар від вузла — тиша скинута.
void health_on_beat(NodeHealth *h, uint32_t now_ms) {
    h->last_beat_ms = now_ms;
    h->missed = 0;
    h->health = NODE_UP;
}

// Викликається періодично (напр., з таймера монітора). Рахує тишу
// й підіймає присуд по щаблях UP -> SUSPECT -> DOWN.
void health_tick(NodeHealth *h, uint32_t now_ms) {
    if (now_ms - h->last_beat_ms < BEAT_PERIOD_MS)
        return;                          // удар устиг у вікно — усе гаразд

    // період минув без удару; зсуваємо «годинник очікування» на період,
    // щоб один пропуск рахувався один раз, а не безперервно
    h->last_beat_ms += BEAT_PERIOD_MS;
    h->missed++;

    if (h->missed >= MISS_LIMIT)      h->health = NODE_DOWN;
    else                              h->health = NODE_SUSPECT;
}
