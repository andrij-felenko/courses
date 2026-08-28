#include <string_view>
#include <memory>

class FeatureFlagService {
public:
    virtual ~FeatureFlagService() = default;
    [[nodiscard]] virtual bool is_enabled(std::string_view flag_key, 
                                          const UserContext& context) const noexcept = 0;
};

void process_transaction(Transaction& tx, 
                         const UserContext& context, 
                         const FeatureFlagService& flags) {
    if (flags.is_enabled("new_payment_v2", context)) {
        execute_payment_v2(tx);
    } else {
        execute_legacy_payment(tx);
    }
}
