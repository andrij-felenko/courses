// stream.cpp
#include "stream.hpp"

// Визначення буфера пам'яті
decltype(g_stream_storage) g_stream_storage;

// Глобальний лічильник кількості одиниць трансляції
static int g_init_count = 0;

StreamInitializer::StreamInitializer() {
    // Якщо це перший модуль, що завантажився — конструюємо об'єкт
    if (g_init_count++ == 0) {
        new (&g_stream_storage) StreamBuffer();
    }
}

StreamInitializer::~StreamInitializer() {
    // Якщо це останній модуль, що завершується — руйнуємо об'єкт
    if (--g_init_count == 0) {
        reinterpret_cast<StreamBuffer*>(&g_stream_storage)->flush();
        reinterpret_cast<StreamBuffer*>(&g_stream_storage)->~StreamBuffer();
    }
}
