// Walking Skeleton Harness мовою C++
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <optional>
#include <chrono>

struct CheckoutRequest {
    std::string trace_id;
    std::string tenant_id;
    std::string idempotency_key;
    double amount;
    std::string currency;
};

struct CheckoutResponse {
    std::string transaction_id;
    std::string trace_id;
    std::string status;
    int http_code;
};

struct OutboxEntry {
    std::string id;
    std::string tenant_id;
    double amount;
    std::chrono::system_clock::time_point timestamp;
};

class IdempotencyStore {
public:
    std::optional<CheckoutResponse> find(std::string_view key) const {
        if (key == "idem-duplicate-123") {
            return CheckoutResponse{
                "tx_cached_998877",
                "cached_trace",
                "DUPLICATE_ACK",
                200
            };
        }
        return std::nullopt;
    }
};

class OutboxJournal {
private:
    std::vector<OutboxEntry> entries_;
public:
    bool append(std::string_view tenant, double amount, std::string_view trace_id, std::string& out_tx_id) {
        out_tx_id = "tx_live_" + std::to_string(entries_.size() + 100);
        entries_.push_back(OutboxEntry{
            out_tx_id,
            std::string(tenant),
            amount,
            std::chrono::system_clock::now()
        });

        std::cout << "[" << trace_id << "] [OUTBOX_APPEND] Tenant: " << tenant 
                  << ", TxID: " << out_tx_id << ", Amount: " << amount << "\n";
        return true;
    }
};

class WalkingSkeletonPipeline {
private:
    IdempotencyStore idempotency_store_;
    OutboxJournal outbox_journal_;

public:
    CheckoutResponse processCheckout(const CheckoutRequest& req) {
        std::cout << "[" << req.trace_id << "] [EDGE_ROUTER] Ingesting request for Tenant: " 
                  << req.tenant_id << ", Key: " << req.idempotency_key << "\n";

        // 1. Guard ідемпотентності
        if (auto cached = idempotency_store_.find(req.idempotency_key)) {
            std::cout << "[" << req.trace_id << "] [IDEMPOTENCY_GUARD] Duplicate key detected. Returning cached response.\n";
            auto res = *cached;
            res.trace_id = req.trace_id;
            return res;
        }

        // 2. Атомарний запис у локальний Ledger Outbox
        std::string tx_id;
        if (!outbox_journal_.append(req.tenant_id, req.amount, req.trace_id, tx_id)) {
            return CheckoutResponse{"", req.trace_id, "OUTBOX_ERROR", 503};
        }

        // 3. Формування відповіді
        std::cout << "[" << req.trace_id << "] [WALKING_SKELETON_SUCCESS] Completed end-to-end trace. Code: 200\n";
        return CheckoutResponse{tx_id, req.trace_id, "SUCCESS", 200};
    }
};

int main() {
    std::cout << "=== OmniPay Walking Skeleton Pipeline Harness (C++) ===\n\n";

    WalkingSkeletonPipeline pipeline;

    CheckoutRequest req1{
        "trace-uuid-1111-aaaa",
        "tenant_enterprise_eu",
        "idem-unique-001",
        250.50,
        "EUR"
    };

    auto res1 = pipeline.processCheckout(req1);
    std::cout << "Result 1: TxID=" << res1.transaction_id << ", Status=" << res1.status << ", Code=" << res1.http_code << "\n\n";

    CheckoutRequest req2{
        "trace-uuid-2222-bbbb",
        "tenant_enterprise_eu",
        "idem-duplicate-123",
        250.50,
        "EUR"
    };

    auto res2 = pipeline.processCheckout(req2);
    std::cout << "Result 2: TxID=" << res2.transaction_id << ", Status=" << res2.status << ", Code=" << res2.http_code << "\n";

    return 0;
}
