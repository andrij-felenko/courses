#include "FreeRTOS.h"
#include "task.h"
#include <cstddef>
#include <cstdint>

/* RAII-обгортка для критичної секції FreeRTOS */
class CriticalSectionGuard {
public:
    CriticalSectionGuard() {
        taskENTER_CRITICAL();
    }
    
    ~CriticalSectionGuard() {
        taskEXIT_CRITICAL();
    }
    
    /* Заборона копіювання та переміщення для безпеки */
    CriticalSectionGuard(const CriticalSectionGuard&) = delete;
    CriticalSectionGuard& operator=(const CriticalSectionGuard&) = delete;
};

struct HardwareBuffer {
    uint8_t data[256];
    size_t head;
    size_t tail;

    bool write_byte(uint8_t byte) {
        /* Автоматичний вхід у критичну секцію при створенні об'єкта */
        CriticalSectionGuard guard;
        
        size_t next_head = (head + 1) % sizeof(data);
        if (next_head == tail) {
            return false; /* Буфер повний, деструктор guard безпечно відновить переривання */
        }
        
        data[head] = byte;
        head = next_head;
        return true;
        /* Деструктор CriticalSectionGuard викликається автоматично при виході з функції */
    }
};
