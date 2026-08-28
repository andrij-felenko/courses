#include <atomic>

// Оголошення: глобальний, видний обом ядрам
std::atomic<uint32_t> events{0};

// Core 0 — збір/мережа: інкремент (relaxed — потрібна лише атомарність, не порядок)
void onDataReady() {
    events.fetch_add(1, std::memory_order_relaxed); // неподільна RMW без замка
}

// Core 1 — loop(): читання свіжого значення
void loop() {
    uint32_t n = events.load(std::memory_order_relaxed); // атомарне читання
    display(n);

    // Для порівняння — те саме спінлоком (надмірно для одного слова):
    // portENTER_CRITICAL(&mux); n = events++; portEXIT_CRITICAL(&mux);
}
