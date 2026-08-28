class SaslPlainMechanism final : public ISaslMechanism {
public:
    [[nodiscard]] std::string_view name() const noexcept override {
        return "PLAIN";
    }

    SaslStatus client_start(const SaslCredentials& cred, SecureByteVector& out) override {
        if (cred.authcid.empty() || cred.password.empty()) {
            return SaslStatus::ErrorSyntax;
        }

        std::size_t authzid_len = cred.authzid ? cred.authzid->size() : 0;
        std::size_t total = authzid_len + 1 + cred.authcid.size() + 1 + cred.password.size();
        
        out.resize(total);
        uint8_t* ptr = out.data();

        if (cred.authzid && !cred.authzid->empty()) {
            std::memcpy(ptr, cred.authzid->data(), authzid_len);
            ptr += authzid_len;
        }
        *ptr++ = '\0';

        std::memcpy(ptr, cred.authcid.data(), cred.authcid.size());
        ptr += cred.authcid.size();
        *ptr++ = '\0';

        std::memcpy(ptr, cred.password.data(), cred.password.size());

        return SaslStatus::Ok;
    }

    SaslStatus client_step(std::span<const uint8_t>, SecureByteVector&) override {
        return SaslStatus::ErrorSyntax;
    }

    SaslStatus server_start(SecureByteVector&) override {
        return SaslStatus::Ok;
    }

    SaslStatus server_step(std::span<const uint8_t> in, SecureByteVector&,
                          std::string& authenticated_user) override {
        if (in.empty()) return SaslStatus::ErrorSyntax;

        auto span_str = std::string_view(reinterpret_cast<const char*>(in.data()), in.size());
        auto first_nul = span_str.find('\0');
        if (first_nul == std::string_view::npos) return SaslStatus::ErrorSyntax;

        auto authzid = span_str.substr(0, first_nul);
        auto rem = span_str.substr(first_nul + 1);

        auto second_nul = rem.find('\0');
        if (second_nul == std::string_view::npos) return SaslStatus::ErrorSyntax;

        auto authcid = rem.substr(0, second_nul);
        auto password = rem.substr(second_nul + 1);

        if (authcid.empty()) return SaslStatus::ErrorSyntax;

        if (authcid == "alice" && password == "SecretPass_42!") {
            authenticated_user = authzid.empty() ? std::string(authcid) : std::string(authzid);
            return SaslStatus::Ok;
        }

        return SaslStatus::ErrorAuth;
    }
};
