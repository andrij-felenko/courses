#include "HatMonitor.hpp"

#include <iostream>
#include <stdexcept>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>

// Зовнішнє оголошення для I2C ioctl команд Linux kernel
extern "C" {
#include <linux/i2c-dev.h>
#ifndef I2C_SLAVE
#define I2C_SLAVE 0x0703
#endif
}

HatMonitor::HatMonitor(std::string_view device, uint8_t slave_addr)
    : fd_(-1), slave_addr_(slave_addr), contact_degraded_(false) {
    initBus(device);
}

HatMonitor::HatMonitor(HatMonitor&& other) noexcept
    : fd_(other.fd_),
      slave_addr_(other.slave_addr_),
      config_(other.config_),
      stats_(other.stats_),
      contact_degraded_(other.contact_degraded_) {
    other.fd_ = -1;
}

HatMonitor& HatMonitor::operator=(HatMonitor&& other) noexcept {
    if (this != &other) {
        if (fd_ >= 0) {
            close(fd_);
        }
        fd_ = other.fd_;
        slave_addr_ = other.slave_addr_;
        config_ = other.config_;
        stats_ = other.stats_;
        contact_degraded_ = other.contact_degraded_;
        other.fd_ = -1;
    }
    return *this;
}

HatMonitor::~HatMonitor() {
    if (fd_ >= 0) {
        close(fd_);
    }
}

void HatMonitor::initBus(std::string_view device) {
    std::string device_path(device);
    fd_ = open(device_path.c_str(), O_RDWR);
    if (fd_ < 0) {
        // У навчальному середовищі або при відсутності реального заліза /dev/i2c-1
        // можемо симулювати або кидати виняток. Для робастності зафіксуємо помилку у stderr
        // та встановимо fd_ у -1, але для демонстрації RAII кинемо system_error.
        throw std::system_error(errno, std::generic_category(), 
            "Не вдалося відкрити шину I2C: " + device_path);
    }

    if (ioctl(fd_, I2C_SLAVE, slave_addr_) < 0) {
        int saved_errno = errno;
        close(fd_);
        fd_ = -1;
        throw std::system_error(saved_errno, std::generic_category(), 
            "Не вдалося встановити I2C адресу веденого пристрою");
    }
}

bool HatMonitor::probe() {
    stats_.total_queries++;
    
    // Спроба виконати порожній запит (SMBus quick command або простий write з 0 байтів)
    // У Linux i2c-dev зазвичай використовують i2c_smbus_write_quick або звичайний write.
    char dummy = 0;
    ssize_t res = write(fd_, &dummy, 1);
    
    if (res < 0) {
        // Аналізуємо причину збою транзакції
        if (errno == ENXIO) {
            stats_.ack_failures++; // Відсутність ACK від шилда (немає контакту)
        } else if (errno == ETIMEDOUT) {
            stats_.timeouts++;     // Тайм-аут шини (проблеми з підтягуючими резисторами)
        } else {
            stats_.bus_errors++;   // Апаратна помилка шини (брязкіт, коротке замикання)
        }
        return false;
    }
    return true;
}

std::optional<std::vector<uint8_t>> HatMonitor::readRegister(uint8_t reg, size_t length) {
    stats_.total_queries++;

    // Запис адреси регістру, з якого читаємо
    ssize_t written = write(fd_, &reg, 1);
    if (written != 1) {
        stats_.ack_failures++;
        return std::nullopt;
    }

    std::vector<uint8_t> buffer(length);
    ssize_t read_bytes = read(fd_, buffer.data(), length);
    if (read_bytes != static_cast<ssize_t>(length)) {
        stats_.bus_errors++;
        return std::nullopt;
    }

    return buffer;
}

void HatMonitor::runStressTest(size_t cycles) {
    std::cout << "[HatMonitor] Запуск стрес-тесту на " << cycles << " циклів для адреси 0x" 
              << std::hex << static_cast<int>(slave_addr_) << std::dec << "...\n";

    for (size_t i = 0; i < cycles; ++i) {
        // Проводимо опитування стану
        bool ok = probe();
        if (!ok && (stats_.ack_failures > 5 || stats_.bus_errors > 3)) {
            contact_degraded_ = true;
        }
        
        // Невелика пауза між опитуваннями (симуляція апаратного такту)
        usleep(10000); // 10 мс
    }
}

void HatMonitor::printReport() const {
    std::cout << "\n===== ЗВІТ МОНІТОРИНГУ МІЖПЛАТНОГО СТЕКА М2.5 =====\n";
    std::cout << "Загальна кількість транзакцій: " << stats_.total_queries << "\n";
    std::cout << "Відмови ACK (проблеми механічного контакту): " << stats_.ack_failures << "\n";
    std::cout << "Тайм-аути шини I2C: " << stats_.timeouts << "\n";
    std::cout << "Апаратні помилки шини (брязкіт ліній): " << stats_.bus_errors << "\n";
    
    double error_rate = 0.0;
    if (stats_.total_queries > 0) {
        error_rate = static_cast<double>(stats_.ack_failures + stats_.bus_errors) / stats_.total_queries * 100.0;
    }
    std::cout << "Рівень помилок зв'язку: " << error_rate << "%\n";

    std::cout << "\n--- ЕКСПЕРТНИЙ ВИСНОВОК ЩОДО МОНТАЖУ СТЕКА ---\n";
    if (contact_degraded_ || error_rate > 5.0) {
        std::cout << "[ПОПЕРЕДЖЕННЯ] Виявлено нестабільність електричного контакту на стійках М2.5!\n"
                  << "Рекомендації:\n"
                  << "1. Перевірте момент затягування нікельованих гвинтів та стійок М2.5 (можливий перекіс або недотяг).\n"
                  << "2. Очистіть контактні площадки плат від окислення.\n"
                  << "3. Перевірте номінал підтягуючих резисторів (Pull-up) на лініях SDA/SCL через ємність монтажу.\n";
    } else {
        std::cout << "[ОК] Механічний монтаж та електричний контакт у стеку стабільні.\n"
                  << "Якість з'єднання відповідає технічним вимогам набору М2.5.\n";
    }
    std::cout << "====================================================\n";
}
