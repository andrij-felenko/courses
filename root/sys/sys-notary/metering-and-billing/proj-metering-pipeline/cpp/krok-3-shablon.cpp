struct Reservation {
    std::string reservation_id;
    std::string tenant_id;
    CurrencyMicros reserved_micros;
    bool is_active;
};

class CreditQuotaManager {
private:
    CurrencyMicros available_balance_micros_;
    CurrencyMicros locked_hold_micros_;

public:
    explicit CreditQuotaManager(CurrencyMicros initial_balance)
        : available_balance_micros_(initial_balance), locked_hold_micros_(0) {}

    // Фаза 1: Резервування ліміту
    std::optional<Reservation> acquire_hold(std::string_view tenant_id, 
                                            std::string_view reservation_id, 
                                            CurrencyMicros estimated_max_cost) {
        if (estimated_max_cost <= 0) return std::nullopt;

        // Перевіряємо чистий доступний баланс з урахуванням інших активних холдів
        if (available_balance_micros_ < estimated_max_cost) {
            return std::nullopt; // Недостатньо коштів для гарантованого старту
        }

        available_balance_micros_ -= estimated_max_cost;
        locked_hold_micros_ += estimated_max_cost;

        return Reservation{
            std::string(reservation_id),
            std::string(tenant_id),
            estimated_max_cost,
            true
        };
    }

    // Фаза 3а: Фіналізація фактичного споживання
    bool settle_hold(Reservation& res, CurrencyMicros actual_cost) {
        if (!res.is_active || actual_cost > res.reserved_micros || actual_cost < 0) {
            return false;
        }

        CurrencyMicros unused_funds = res.reserved_micros - actual_cost;
        locked_hold_micros_ -= res.reserved_micros;
        
        // Повертаємо невикористану різницю назад у доступний баланс
        available_balance_micros_ += unused_funds;
        res.is_active = false;
        return true;
    }

    // Фаза 3б: Скасування та вивільнення в разі помилки
    void release_hold(Reservation& res) {
        if (!res.is_active) return;
        locked_hold_micros_ -= res.reserved_micros;
        available_balance_micros_ += res.reserved_micros;
        res.is_active = false;
    }

    CurrencyMicros get_available_balance() const { return available_balance_micros_; }
};
