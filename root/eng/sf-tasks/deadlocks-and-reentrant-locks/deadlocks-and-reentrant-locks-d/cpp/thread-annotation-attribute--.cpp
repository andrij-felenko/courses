// Приклад анотування C++ коду для статичного аналізу Clang
#include "macro_defs.h"

class THREAD_ANNOTATION_ATTRIBUTE__(capability("mutex")) StaticLock {
public:
    void Lock() THREAD_ANNOTATION_ATTRIBUTE__(exclusive_lock_function());
    void Unlock() THREAD_ANNOTATION_ATTRIBUTE__(unlock_function());
};

class SensorDriver {
private:
    StaticLock lock_;
    uint32_t raw_adc_data_ THREAD_ANNOTATION_ATTRIBUTE__(guarded_by(lock_));

public:
    void update_sensor() {
        lock_.Lock();
        raw_adc_data_ = 1024; // Безпечний доступ усередині критичної секції
        lock_.Unlock();
    }

    uint32_t read_uncached() {
        // Компілятор згенерує синтаксичну помилку при спробі прямого читання без захоплення lock_
        return raw_adc_data_; 
    }
};
