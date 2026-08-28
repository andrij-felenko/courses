#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <cstdint>
#include <cmath>

enum class OrderStatus {
    Pending,
    Paid,
    Canceled,
    Refunded
};

struct OrderRecord {
    std::string id;
    OrderStatus status;
    int64_t amount_cents;
};

struct LedgerLine {
    std::string account_id;
    int64_t debit_cents;
    int64_t credit_cents;
};

class OrderFulfillmentCoordinator {
private:
    std::unordered_set<std::string> processed_event_ids_;
    std::unordered_map<std::string, OrderRecord> orders_;
    std::vector<LedgerLine> ledger_;

public:
    OrderFulfillmentCoordinator() {
        orders_["ord_884920"] = OrderRecord{
            .id = "ord_884920",
            .status = OrderStatus::Pending,
            .amount_cents = 10990
        };
    }

    std::string handle_payment_succeeded(const std::string& event_id,
                                         const std::string& order_id,
                                         int64_t amount_cents) {
        // 1. Дедуплікація подій
        if (processed_event_ids_.contains(event_id)) {
            return "ALREADY_PROCESSED";
        }

        auto it = orders_.find(order_id);
        if (it == orders_.end()) {
            return "ORDER_NOT_FOUND";
        }

        // 2. Монотонний захист станів (State Guard)
        if (it->second.status == OrderStatus::Paid) {
            processed_event_ids_.insert(event_id);
            return "IGNORED_OLD_STATE";
        }

        // 3. Зміна стану та подвійний бухгалтерський запис
        it->second.status = OrderStatus::Paid;
        const int64_t fee = static_cast<int64_t>(std::round(amount_cents * 0.029 + 30));

        ledger_.push_back(LedgerLine{.account_id = "1010-PSP-CLEARING", .debit_cents = amount_cents, .credit_cents = 0});
        ledger_.push_back(LedgerLine{.account_id = "4010-SALES-REVENUE", .debit_cents = 0, .credit_cents = amount_cents});
        ledger_.push_back(LedgerLine{.account_id = "5010-GATEWAY-EXPENSE", .debit_cents = fee, .credit_cents = 0});
        ledger_.push_back(LedgerLine{.account_id = "1010-PSP-CLEARING", .debit_cents = 0, .credit_cents = fee});

        processed_event_ids_.insert(event_id);
        return "PROCESSED";
    }

    [[nodiscard]] int64_t get_account_net_balance(const std::string& account_id) const {
        int64_t balance = 0;
        for (const auto& line : ledger_) {
            if (line.account_id == account_id) {
                balance += (line.debit_cents - line.credit_cents);
            }
        }
        return balance;
    }
};
