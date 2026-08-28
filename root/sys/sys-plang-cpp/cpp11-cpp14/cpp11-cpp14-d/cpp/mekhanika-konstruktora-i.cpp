#include <iostream>
#include <vector>
#include <utility>

class HeavyBuffer {
private:
    size_t m_size;
    int*   m_data;

public:
    // Звичайний конструктор виділення
    explicit HeavyBuffer(size_t size) 
        : m_size(size), m_data(new int[size]) {}

    // Деструктор RAII
    ~HeavyBuffer() {
        delete[] m_data;
    }

    // 1. Конструктор копіювання: глибоке виділення O(N)
    HeavyBuffer(const HeavyBuffer& other) 
        : m_size(other.m_size), m_data(new int[other.m_size]) {
        for (size_t i = 0; i < m_size; ++i) {
            m_data[i] = other.m_data[i];
        }
    }

    // 2. Конструктор переміщення: відчуження ресурсу O(1)
    HeavyBuffer(HeavyBuffer&& other) noexcept 
        : m_size(other.m_size), m_data(other.m_data) {
        // Обнулення вихідного об'єкта: перехід у стан moved-from
        other.m_size = 0;
        other.m_data = nullptr;
    }

    // 3. Оператор присвоєння переміщенням
    HeavyBuffer& operator=(HeavyBuffer&& other) noexcept {
        if (this != &other) {
            delete[] m_data; // Звільнення власного старого ресурсу
            m_size = other.m_size;
            m_data = other.m_data;
            other.m_size = 0;
            other.m_data = nullptr;
        }
        return *this;
    }
};
