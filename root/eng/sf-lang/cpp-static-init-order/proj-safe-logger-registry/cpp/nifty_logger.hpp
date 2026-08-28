// nifty_logger.hpp
#pragma once
#include <iostream>
#include <new>

class NiftyLogger {
public:
    void log(const char* msg) const {
        std::cout << "[NIFTY] " << msg << "\n";
    }
};

// Буфер сирої пам'яті для запобігання неконтрольованого виклику конструктора
extern alignas(NiftyLogger) char g_nifty_storage[];
#define g_nifty_logger (*reinterpret_cast<NiftyLogger*>(g_nifty_storage))

// Клас-ініціалізатор у заголовку
class NiftyInitializer {
public:
    NiftyInitializer();
    ~NiftyInitializer();
};

// Кожна одиниця трансляції отримує власну статичну копію
static NiftyInitializer s_nifty_init;
