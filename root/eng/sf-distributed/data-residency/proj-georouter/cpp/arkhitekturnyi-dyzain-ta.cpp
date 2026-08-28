#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <optional>
#include <expected>
#include <cstdint>
#include <algorithm>
#include <span>

namespace georouter {

enum class JurisdictionId : int8_t {
    EuEea = 0,
    UsFed = 1,
    Apac  = 2,
    Unknown = -1
};

enum class EgressPolicy : uint8_t {
    Forbidden = 0,
    PermittedPseudonymized = 1,
    Unrestricted = 2
};

enum class RouterError : uint8_t {
    JurisdictionUnknown,
    CrossBorderViolation,
    TokenizationFailed,
    BufferOverflow
};

struct JurisdictionConfig {
    JurisdictionId id;
    std::string name;
    std::vector<std::string> allowed_regions;
    EgressPolicy egress_policy;
    std::string hsm_key_salt;
};

struct TransactionRequest {
    std::string transaction_id;
    std::string country_code;
    std::string tenant_id;
    std::string customer_name;
    std::string customer_iban;
    double amount{0.0};
    std::string target_datacenter;
};

struct AnonymizedEvent {
    std::string transaction_id;
    JurisdictionId jurisdiction;
    std::string name_token;
    std::string iban_token;
    double amount{0.0};
    bool is_compliant{false};
};

} // namespace georouter
