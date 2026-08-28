// Заголовок LegacyBuffer.h
template <typename T>
class LegacyBuffer {
    T* storage;
    size_t length;

public:
    void reset() {
        // ПОМИЛКА 1 у C++20: ZeroMemory не знайдено на Фазі 1 (відсутній інклуд windows.h)
        ZeroMemory(storage, length * sizeof(T));

        // ПОМИЛКА 2 у C++20: typename обов'язковий перед залежним типом T::iterator
        T::iterator it = storage->begin();
    }
};

#include <windows.h> // Помилка архітектури: системний заголовок включено ПІСЛЯ шаблону!
