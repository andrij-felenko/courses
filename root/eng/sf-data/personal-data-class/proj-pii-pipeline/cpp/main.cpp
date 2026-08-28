#include <iostream>
#include <string>
#include <string_view>
#include <format>
#include <sstream>
#include <cstdint>

enum class UserRole {
    Admin,
    Analyst,
    Auditor
};

enum class DataClassification {
    Public,
    DirectPii,
    QuasiIdentifier,
    Sensitive
};

struct UserRecord {
    std::string email;
    std::string card_number;
    uint32_t age{};
    std::string zip_code;
    std::string diagnosis;
};

struct TransformedRecord {
    std::string email;
    std::string card_number;
    std::string age;
    std::string zip_code;
    std::string diagnosis;
};

class PrivacyEngine {
public:
    explicit PrivacyEngine(std::string_view salt) : salt_(salt) {}

    [[nodiscard]] std::string tokenize(std::string_view input) const {
        uint64_t hash = 0xcbf29ce484222325ULL;
        constexpr uint64_t prime = 0x100000001b3ULL;

        for (char c : salt_) {
            hash ^= static_cast<uint64_t>(static_cast<unsigned char>(c));
            hash *= prime;
        }
        for (char c : input) {
            hash ^= static_cast<uint64_t>(static_cast<unsigned char>(c));
            hash *= prime;
        }
        std::stringstream ss;
        ss << "tok_" << std::hex << hash;
        return ss.str();
    }

    [[nodiscard]] static std::string mask_email(std::string_view email) {
        const auto at_pos = email.find('@');
        if (at_pos == std::string_view::npos || at_pos == 0) {
            return "******";
        }
        if (at_pos <= 2) {
            return std::string("*") + std::string(email.substr(at_pos));
        }
        return std::string(1, email.front()) + "***" + 
               std::string(1, email[at_pos - 1]) + 
               std::string(email.substr(at_pos));
    }

    [[nodiscard]] static std::string mask_card(std::string_view card) {
        if (card.length() < 4) {
            return "****";
        }
        return "****-****-****-" + std::string(card.substr(card.length() - 4));
    }

    [[nodiscard]] static std::string bucket_age(uint32_t age) {
        const uint32_t lower = (age / 10) * 10;
        const uint32_t upper = lower + 9;
        return std::to_string(lower) + "–" + std::to_string(upper);
    }

    [[nodiscard]] static std::string bucket_zip(std::string_view zip) {
        if (zip.length() <= 2) {
            return "***";
        }
        return std::string(zip.substr(0, 3)) + "**";
    }

    [[nodiscard]] TransformedRecord process(const UserRecord& in, UserRole role) const {
        TransformedRecord out;
        switch (role) {
            case UserRole::Admin:
                out.email = in.email;
                out.card_number = in.card_number;
                out.age = std::to_string(in.age);
                out.zip_code = in.zip_code;
                out.diagnosis = in.diagnosis;
                break;

            case UserRole::Analyst:
                out.email = mask_email(in.email);
                out.card_number = mask_card(in.card_number);
                out.age = bucket_age(in.age);
                out.zip_code = bucket_zip(in.zip_code);
                out.diagnosis = in.diagnosis;
                break;

            case UserRole::Auditor:
                out.email = tokenize(in.email);
                out.card_number = tokenize(in.card_number);
                out.age = "[SUPPRESSED]";
                out.zip_code = bucket_zip(in.zip_code);
                out.diagnosis = "[PROTECTED]";
                break;
        }
        return out;
    }

private:
    std::string salt_;
};

int main() {
    const UserRecord user{
        .email = "william.weld@mass.gov",
        .card_number = "4111555588880213",
        .age = 48,
        .zip_code = "02138",
        .diagnosis = "Type-2 Diabetes"
    };

    const PrivacyEngine engine("k9_vault_pepper_2026");

    const auto analyst_view = engine.process(user, UserRole::Analyst);
    std::cout << "=== РОЛЬ: ANALYST ===\n"
              << "Email: " << analyst_view.email << "\n"
              << "Card:  " << analyst_view.card_number << "\n"
              << "Age:   " << analyst_view.age << "\n"
              << "ZIP:   " << analyst_view.zip_code << "\n"
              << "Diag:  " << analyst_view.diagnosis << "\n\n";

    const auto auditor_view = engine.process(user, UserRole::Auditor);
    std::cout << "=== РОЛЬ: AUDITOR ===\n"
              << "Email: " << auditor_view.email << "\n"
              << "Card:  " << auditor_view.card_number << "\n"
              << "Age:   " << auditor_view.age << "\n"
              << "ZIP:   " << auditor_view.zip_code << "\n"
              << "Diag:  " << auditor_view.diagnosis << "\n";

    return 0;
}
