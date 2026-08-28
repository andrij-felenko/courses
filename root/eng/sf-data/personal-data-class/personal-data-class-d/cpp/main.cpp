#include <iostream>
#include <string>
#include <string_view>
#include <sstream>
#include <cstdint>
#include <iomanip>

enum class AccessRole {
    Admin,
    Analyst,
    Auditor
};

struct IngestionRecord {
    std::string email;
    std::string card_pan;
    uint32_t age{};
    std::string zip_code;
    std::string diagnosis;
};

struct SanitizedRecord {
    std::string email;
    std::string card_pan;
    std::string age;
    std::string zip_code;
    std::string diagnosis;
};

class PrivacyProcessor {
public:
    explicit PrivacyProcessor(std::string_view pepper) : pepper_(pepper) {}

    [[nodiscard]] std::string tokenize(std::string_view value) const {
        uint64_t hash = 0xcbf29ce484222325ULL;
        constexpr uint64_t prime = 0x100000001b3ULL;

        for (char c : pepper_) {
            hash = (hash ^ static_cast<uint64_t>(static_cast<unsigned char>(c))) * prime;
        }
        for (char c : value) {
            hash = (hash ^ static_cast<uint64_t>(static_cast<unsigned char>(c))) * prime;
        }
        std::stringstream ss;
        ss << "tok_" << std::hex << std::setw(16) << std::setfill('0') << hash;
        return ss.str();
    }

    [[nodiscard]] static std::string mask_email(std::string_view email) {
        const auto at = email.find('@');
        if (at == std::string_view::npos || at == 0) {
            return "***@***";
        }
        if (at <= 2) {
            return std::string("*") + std::string(email.substr(at));
        }
        return std::string(1, email.front()) + "***" + 
               std::string(1, email[at - 1]) + 
               std::string(email.substr(at));
    }

    [[nodiscard]] static std::string generalize_age(uint32_t age) {
        const uint32_t lower = (age / 10) * 10;
        return std::to_string(lower) + "–" + std::to_string(lower + 9);
    }

    [[nodiscard]] static std::string generalize_zip(std::string_view zip) {
        if (zip.length() < 3) {
            return "***";
        }
        return std::string(zip.substr(0, 3)) + "**";
    }

    [[nodiscard]] SanitizedRecord transform(const IngestionRecord& in, AccessRole role) const {
        SanitizedRecord out;
        switch (role) {
            case AccessRole::Admin:
                out.email = in.email;
                out.card_pan = in.card_pan;
                out.age = std::to_string(in.age);
                out.zip_code = in.zip_code;
                out.diagnosis = in.diagnosis;
                break;

            case AccessRole::Analyst:
                out.email = mask_email(in.email);
                out.card_pan = in.card_pan.length() >= 4 
                    ? "****-****-****-" + in.card_pan.substr(in.card_pan.length() - 4) 
                    : "****";
                out.age = generalize_age(in.age);
                out.zip_code = generalize_zip(in.zip_code);
                out.diagnosis = in.diagnosis;
                break;

            case AccessRole::Auditor:
                out.email = tokenize(in.email);
                out.card_pan = tokenize(in.card_pan);
                out.age = "[SUPPRESSED]";
                out.zip_code = generalize_zip(in.zip_code);
                out.diagnosis = "[REDACTED]";
                break;
        }
        return out;
    }

private:
    std::string pepper_;
};

int main() {
    const IngestionRecord raw{
        .email = "alisa.shevchenko@cyber.ua",
        .card_pan = "5168742299014588",
        .age = 34,
        .zip_code = "01001",
        .diagnosis = "Acute Bronchitis"
    };

    const PrivacyProcessor processor("sec_pepper_v2_2026");

    const auto analyst_res = processor.transform(raw, AccessRole::Analyst);
    std::cout << "=== РОЛЬ: ANALYST ===\n"
              << "Email: " << analyst_res.email << " | Card: " << analyst_res.card_pan
              << " | Age: " << analyst_res.age << " | ZIP: " << analyst_res.zip_code
              << " | Diag: " << analyst_res.diagnosis << "\n\n";

    const auto auditor_res = processor.transform(raw, AccessRole::Auditor);
    std::cout << "=== РОЛЬ: AUDITOR ===\n"
              << "Email: " << auditor_res.email << " | Card: " << auditor_res.card_pan
              << " | Age: " << auditor_res.age << " | ZIP: " << auditor_res.zip_code
              << " | Diag: " << auditor_res.diagnosis << "\n";

    return 0;
}
