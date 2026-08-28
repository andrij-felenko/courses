struct LedgerEntry {
    std::string transaction_id;
    std::string account_id;
    std::string account_type;
    CurrencyMicros amount_micros; // додатне = збільшення, від'ємне = зменшення
    std::string reference_id;
};

class DoubleEntryLedger {
private:
    std::vector<LedgerEntry> entries_;

public:
    bool record_usage_charge(const std::string& transaction_id,
                             const std::string& tenant_id,
                             CurrencyMicros amount_micros,
                             const std::string& event_ref) {
        if (amount_micros <= 0) return false;

        std::string liability_account = "liability:" + tenant_id;
        std::string revenue_account = "revenue:api_compute";

        // Проводка 1: Дебет зобов'язань клієнта (зменшення депозиту на -amount)
        entries_.push_back(LedgerEntry{
            transaction_id,
            liability_account,
            "liability",
            -amount_micros,
            event_ref
        });

        // Проводка 2: Кредит доходів платформи (збільшення виручки на +amount)
        entries_.push_back(LedgerEntry{
            transaction_id,
            revenue_account,
            "revenue",
            amount_micros,
            event_ref
        });

        return true;
    }

    // Розрахунок поточного балансу рахунку через згортку журналу
    CurrencyMicros get_account_balance(const std::string& account_id) const {
        CurrencyMicros balance = 0;
        for (const auto& entry : entries_) {
            if (entry.account_id == account_id) {
                balance += entry.amount_micros;
            }
        }
        return balance;
    }

    // Аудиторська перевірка балансу реєстру: сума всіх транзакцій має дорівнювати 0
    bool verify_audit_invariant() const {
        CurrencyMicros net_sum = 0;
        for (const auto& entry : entries_) {
            net_sum += entry.amount_micros;
        }
        return net_sum == 0;
    }
};
