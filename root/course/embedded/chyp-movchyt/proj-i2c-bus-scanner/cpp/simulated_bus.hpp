/* Модель шини замість заліза: тип задовольняє концепт OpenDrainLines,
   тож той самий ведучий працює і на платі, і на робочій машині.
   Рівень лінії з відкритим стоком — логічне І всіх причеплених:
   високий дає підтяжка, будь-хто один може притиснути лінію в нуль. */
#pragma once

#include <cstdint>
#include <print>

class SimulatedBus {
public:
    enum class Fault {
        none,           /* справна шина з одним сенсором */
        sda_stuck_low,  /* ведений завис посеред байта й тримає SDA */
        no_pullups,     /* підтяжок немає: лінії нікуди не піднімаються */
        no_power        /* лінії чисті, але сенсор не заживлений */
    };

    SimulatedBus(std::uint8_t slave_addr7, Fault fault)
        : slave_addr_{slave_addr7},
          fault_{fault},
          slave_stuck_{fault == Fault::sda_stuck_low},
          slave_sda_low_{fault == Fault::sda_stuck_low} {
        prev_scl_ = scl_level();
        prev_sda_ = sda_level();
    }

    void take_pins() { std::println("Виводи SCL/SDA переведено в GPIO (апаратний блок I2C вимкнено)"); }
    void give_pins_back() { std::println("Виводи SCL/SDA повернуто апаратному блоку I2C"); }

    void scl_release() { master_scl_low_ = false; step(); }
    void scl_drive_low() { master_scl_low_ = true; step(); }
    [[nodiscard]] bool scl_read() { return scl_level(); }

    void sda_release() { master_sda_low_ = false; step(); }
    void sda_drive_low() { master_sda_low_ = true; step(); }
    [[nodiscard]] bool sda_read() { return sda_level(); }

    void delay_us(std::uint32_t) {
        /* На платі тут крутиться цикл затримки або читається таймер.
           Модель безчасова: автомат рухають фронти, а не мікросекунди. */
    }

private:
    enum class Slave { idle, rx_addr, ack_setup, ack_hold, wait_stop };

    /* Скільки тактів SCL потрібно зависшому веденому, щоб виштовхнути
       рештки свого байта й нарешті відпустити SDA. */
    static constexpr unsigned stuck_clocks_to_release = 5;

    [[nodiscard]] bool scl_level() const {
        if (fault_ == Fault::no_pullups) {
            return false; /* без підтяжки відпущена лінія просто висить у нулі */
        }
        return !master_scl_low_;
    }

    [[nodiscard]] bool sda_level() const {
        if (fault_ == Fault::no_pullups) {
            return false;
        }
        return !(master_sda_low_ || slave_sda_low_);
    }

    /* Один крок автомата: викликається після кожної зміни ліній ведучим */
    void step() {
        const bool scl = scl_level();
        const bool sda = sda_level();
        const bool scl_rise = scl && !prev_scl_;
        const bool scl_fall = !scl && prev_scl_;

        if (slave_stuck_) {
            /* Поки чіп не догнав свій байт, він глухий до START і STOP */
            if (scl_rise && ++stuck_clocks_ >= stuck_clocks_to_release) {
                slave_stuck_ = false;
                slave_sda_low_ = false;
            }
        } else if (scl && prev_scl_ && sda != prev_sda_) {
            /* Перепад SDA при високому SCL — це службова умова, а не дані */
            if (!sda) {
                state_ = Slave::rx_addr;
                shift_ = 0;
                bits_ = 0;
            } else {
                state_ = Slave::idle;
            }
        } else if (scl_rise && state_ == Slave::rx_addr) {
            shift_ = static_cast<std::uint8_t>((shift_ << 1) | (sda ? 1U : 0U));
            if (++bits_ == 8) {
                state_ = Slave::ack_setup;
            }
        } else if (scl_fall) {
            if (state_ == Slave::ack_setup) {
                if (fault_ != Fault::no_power && static_cast<std::uint8_t>(shift_ >> 1) == slave_addr_) {
                    slave_sda_low_ = true; /* ACK виставляється до дев'ятого такту */
                    state_ = Slave::ack_hold;
                } else {
                    state_ = Slave::wait_stop; /* чужа адреса — мовчимо */
                }
            } else if (state_ == Slave::ack_hold) {
                slave_sda_low_ = false; /* дев'ятий такт минув, лінію віддано */
                state_ = Slave::wait_stop;
            }
        }

        prev_scl_ = scl;
        prev_sda_ = sda_level(); /* рівень міг змінитися просто зараз, через ACK */
    }

    std::uint8_t slave_addr_;
    Fault fault_;

    bool master_scl_low_ = false;
    bool master_sda_low_ = false;
    bool slave_stuck_ = false;
    bool slave_sda_low_ = false;

    bool prev_scl_ = true;
    bool prev_sda_ = true;

    Slave state_ = Slave::idle;
    std::uint8_t shift_ = 0;
    unsigned bits_ = 0;
    unsigned stuck_clocks_ = 0;
};
