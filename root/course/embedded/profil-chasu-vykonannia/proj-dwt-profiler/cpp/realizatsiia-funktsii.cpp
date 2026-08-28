// Приклад використання C++ RAII ScopedTimer у реальній задачі
#include "dwt_profiler.hpp"

namespace {
    embedded::profiler::ExecutionStats g_fir_filter_stats;
}

void process_audio_frame(float* buffer, size_t size) {
    // Автоматичний старт заміру при вході в область видимості
    embedded::profiler::ScopedTimer timer(g_fir_filter_stats);

    // Досліджуваний критичний код
    for (size_t i = 0; i < size; ++i) {
        buffer[i] = buffer[i] * 0.5f + 0.1f;
    }
    // Таймер зупиняється в деструкторі, статистика оновлюється автоматично
}
