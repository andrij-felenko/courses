// stream.hpp
#pragma once
#include <new>
#include <type_traits>

class StreamBuffer {
public:
    void write(const char* str);
    void flush();
};

// Буфер сирої пам'яті
extern typename std::aligned_storage<sizeof(StreamBuffer), alignof(StreamBuffer)>::type g_stream_storage;

// Прозоре глобальне посилання для користувача
#define g_stream (*reinterpret_cast<StreamBuffer*>(&g_stream_storage))

// Клас лічильника
class StreamInitializer {
public:
    StreamInitializer();
    ~StreamInitializer();
};

// Статичний об'єкт у кожному .cpp, що підключає stream.hpp
static StreamInitializer s_stream_init;
