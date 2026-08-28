namespace georouter {

class RouterEngine {
public:
    void add_jurisdiction(JurisdictionConfig config) {
        configs_.push_back(std::move(config));
    }

    [[nodiscard]] static JurisdictionId resolve_jurisdiction(std::string_view country_code) noexcept {
        if (country_code == "DE" || country_code == "FR" || country_code == "IT" || country_code == "ES") {
            return JurisdictionId::EuEea;
        }
        if (country_code == "US" || country_code == "CA") {
            return JurisdictionId::UsFed;
        }
        if (country_code == "SG" || country_code == "JP" || country_code == "AU") {
            return JurisdictionId::Apac;
        }
        return JurisdictionId::Unknown;
    }

    [[nodiscard]] std::expected<AnonymizedEvent, RouterError> process_transaction(
        const TransactionRequest& req,
        std::string& log_message
    ) const {
        const auto j_id = resolve_jurisdiction(req.country_code);
        if (j_id == JurisdictionId::Unknown) {
            log_message = "ВІДХИЛЕНО: Невідома юрисдикція для країни: " + req.country_code;
            return std::unexpected(RouterError::JurisdictionUnknown);
        }

        const auto it = std::find_if(configs_.begin(), configs_.end(),
            [j_id](const JurisdictionConfig& c) { return c.id == j_id; });

        if (it == configs_.end()) {
            log_message = "ВІДХИЛЕНО: Відсутня конфігурація для юрисдикції";
            return std::unexpected(RouterError::JurisdictionUnknown);
        }

        const auto& cfg = *it;

        const bool region_valid = std::any_of(
            cfg.allowed_regions.begin(),
            cfg.allowed_regions.end(),
            [&req](const std::string& reg) { return reg == req.target_datacenter; }
        );

        if (!region_valid) {
            log_message = "БЛОКУВАННЯ GDPR: Спроба запису даних з " + req.country_code +
                          " у несанкціонований регіон: " + req.target_datacenter;
            return std::unexpected(RouterError::CrossBorderViolation);
        }

        AnonymizedEvent event;
        event.transaction_id = req.transaction_id;
        event.jurisdiction = j_id;
        event.amount = req.amount;
        event.is_compliant = true;
        event.name_token = Tokenizer::generate_token(req.customer_name, cfg.hsm_key_salt);
        event.iban_token = Tokenizer::generate_token(req.customer_iban, cfg.hsm_key_salt);

        log_message = "УСПІШНО: Транзакцію " + req.transaction_id + " зафіксовано у шарді " +
                      req.target_datacenter + " (" + cfg.name + "). Згенеровано токен: " + event.name_token;

        return event;
    }

private:
    std::vector<JurisdictionConfig> configs_;
};

} // namespace georouter
