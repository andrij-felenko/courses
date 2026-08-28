struct PricingTier {
    uint64_t up_to_units;             // UINT64_MAX для останнього рівня (нескінченність)
    CurrencyMicros rate_per_unit_micros;
};

class RatingEngine {
public:
    static CurrencyMicros calculate_graduated_cost(
        uint64_t total_units, 
        const std::vector<PricingTier>& tiers) 
    {
        CurrencyMicros total_cost = 0;
        uint64_t previous_bound = 0;

        for (const auto& tier : tiers) {
            if (total_units <= previous_bound) {
                break;
            }

            uint64_t units_in_tier = 0;
            if (total_units < tier.up_to_units) {
                units_in_tier = total_units - previous_bound;
            } else {
                units_in_tier = tier.up_to_units - previous_bound;
            }

            total_cost += static_cast<CurrencyMicros>(units_in_tier) * tier.rate_per_unit_micros;
            previous_bound = tier.up_to_units;
        }

        return total_cost;
    }
};
