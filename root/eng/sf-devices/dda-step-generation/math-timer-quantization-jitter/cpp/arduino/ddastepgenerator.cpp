#include <Arduino.h>
#include <avr/io.h>
#include <avr/interrupt.h>

// Клас генератора кроків DDA з апаратним буферуванням таймера AVR Timer1
class DDAStepGenerator {
private:
    static constexpr uint8_t STEP_PIN = 9;  // OC1A вихід
    static constexpr uint8_t DDA_SHIFT = 16;
    
    volatile uint32_t step_ratio_fp_; // Крок DDA у Q16.16
    volatile uint32_t accumulator_;   // Акумулятор похибки
    volatile uint16_t base_period_ticks_; // Базовий період у тактах таймера

public:
    DDAStepGenerator() : step_ratio_fp_(0), accumulator_(0), base_period_ticks_(1000) {}

    void begin(uint32_t step_ratio_fp, uint16_t base_period_ticks) {
        step_ratio_fp_ = step_ratio_fp;
        base_period_ticks_ = base_period_ticks;
        
        pinMode(STEP_PIN, OUTPUT);
        
        // Налаштування Timer1 у режим CTC з скиданням по ICR1
        TCCR1A = 0;
        TCCR1B = (1 << WGM13) | (1 << WGM12) | (1 << CS10); // Prescaler = 1
        
        ICR1 = base_period_ticks_; // Запис початкового періоду у буферний регістр
        TIMSK1 = (1 << ICIE1);     // Дозвіл переривання по захопленню/збігу
    }

    // Метод оновлення періоду у перериванні
    inline void handleInterrupt() {
        // Апаратно вихід OC1A перемикається або інвертується
        accumulator_ += step_ratio_fp_;
        uint16_t correction = accumulator_ >> DDA_SHIFT;
        accumulator_ &= ((1UL << DDA_SHIFT) - 1);
        
        // Перезавантаження ICR1 (має апаратний теневий буфер у режимі CTC)
        ICR1 = base_period_ticks_ + correction;
    }
};

static DDAStepGenerator dda_gen;

ISR(TIMER1_CAPT_vect) {
    dda_gen.handleInterrupt();
}
