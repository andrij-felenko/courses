#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_set>
#include <chrono>
#include <expected>
#include <optional>
#include <cstdint>
#include <span>

namespace krb5 {

inline constexpr std::chrono::seconds MaxClockSkew{300};

enum class ErrorCode : int32_t {
    BadIntegrity = 31,
    TicketExpired = 32,
    RepeatDetected = 34,
    PrincipalMismatch = 36,
    ClockSkew = 37
};

struct KeyBlock {
    int32_t keyType{18}; // AES-256
    std::vector<uint8_t> data;
};

struct EncTicketPart {
    std::string cname;
    std::string crealm;
    KeyBlock sessionKey;
    std::chrono::system_clock::time_point authTime;
    std::chrono::system_clock::time_point startTime;
    std::chrono::system_clock::time_point endTime;
};

struct Authenticator {
    std::string cname;
    std::string crealm;
    std::chrono::system_clock::time_point ctime;
    uint32_t cusec{0};
    uint32_t seqNumber{0};
    std::optional<KeyBlock> subKey;
};

struct ReplayRecord {
    std::string cname;
    int64_t ctimeSec;
    uint32_t cusec;
    std::chrono::system_clock::time_point expiry;

    bool operator==(const ReplayRecord& other) const noexcept {
        return ctimeSec == other.ctimeSec &&
               cusec == other.cusec &&
               cname == other.cname;
    }
};

struct ReplayRecordHash {
    size_t operator()(const ReplayRecord& r) const noexcept {
        size_t h1 = std::hash<std::string>{}(r.cname);
        size_t h2 = std::hash<int64_t>{}(r.ctimeSec);
        size_t h3 = std::hash<uint32_t>{}(r.cusec);
        return h1 ^ (h2 << 1) ^ (h3 << 2);
    }
};

class ReplayCache {
public:
    [[nodiscard]] bool checkAndAdd(std::string_view cname,
                                   std::chrono::system_clock::time_point ctime,
                                   uint32_t cusec,
                                   std::chrono::system_clock::time_point now) {
        pruneExpired(now);

        const auto sec = std::chrono::duration_cast<std::chrono::seconds>(
            ctime.time_since_epoch()).count();

        ReplayRecord record{
            .cname = std::string(cname),
            .ctimeSec = sec,
            .cusec = cusec,
            .expiry = now + MaxClockSkew
        };

        if (cache_.contains(record)) {
            return false; // Виявлено спробу повтору
        }

        cache_.insert(std::move(record));
        return true;
    }

private:
    void pruneExpired(std::chrono::system_clock::time_point now) {
        std::erase_if(cache_, [now](const ReplayRecord& r) noexcept {
            return r.expiry <= now;
        });
    }

    std::unordered_set<ReplayRecord, ReplayRecordHash> cache_;
};

class ServerValidator {
public:
    explicit ServerValidator(KeyBlock serviceKey)
        : serviceKey_(std::move(serviceKey)) {}

    [[nodiscard]] std::expected<KeyBlock, ErrorCode> verifyApReq(
        std::span<const uint8_t> rawTicket,
        std::span<const uint8_t> rawAuth,
        std::chrono::system_clock::time_point now = std::chrono::system_clock::now()) {

        // Крок 1: Розшифрування квитка ключем служби
        auto ticketRes = decryptTicket(rawTicket, serviceKey_);
        if (!ticketRes) return std::unexpected(ticketRes.error());
        const auto& ticket = *ticketRes;

        // Крок 2: Перевірка терміну придатності квитка
        if (now > ticket.endTime + MaxClockSkew) {
            return std::unexpected(ErrorCode::TicketExpired);
        }

        // Крок 3: Розшифрування автентифікатора вилученим сесійним ключем
        auto authRes = decryptAuthenticator(rawAuth, ticket.sessionKey);
        if (!authRes) return std::unexpected(authRes.error());
        const auto& auth = *authRes;

        // Крок 4: Звірка ідентифікаторів принципала
        if (ticket.cname != auth.cname || ticket.crealm != auth.crealm) {
            return std::unexpected(ErrorCode::PrincipalMismatch);
        }

        // Крок 5: Перевірка вікна розсинхронізації годинників
        const auto diff = std::chrono::abs(std::chrono::duration_cast<std::chrono::seconds>(now - auth.ctime));
        if (diff > MaxClockSkew) {
            return std::unexpected(ErrorCode::ClockSkew);
        }

        // Крок 6: Перевірка та реєстрація в кеші повторів
        if (!replayCache_.checkAndAdd(auth.cname, auth.ctime, auth.cusec, now)) {
            return std::unexpected(ErrorCode::RepeatDetected);
        }

        // Успіх: повертаємо узгоджений сесійний ключ
        return ticket.sessionKey;
    }

private:
    static std::expected<EncTicketPart, ErrorCode> decryptTicket(
        std::span<const uint8_t> cipher, const KeyBlock& key) {
        if (cipher.empty() || key.data.empty()) {
            return std::unexpected(ErrorCode::BadIntegrity);
        }
        const auto now = std::chrono::system_clock::now();
        return EncTicketPart{
            .cname = "alice@EXAMPLE.ORG",
            .crealm = "EXAMPLE.ORG",
            .sessionKey = KeyBlock{ .keyType = 18, .data = std::vector<uint8_t>(32, 0x4A) },
            .authTime = now - std::chrono::minutes(1),
            .startTime = now - std::chrono::minutes(1),
            .endTime = now + std::chrono::hours(8)
        };
    }

    static std::expected<Authenticator, ErrorCode> decryptAuthenticator(
        std::span<const uint8_t> cipher, const KeyBlock& sessionKey) {
        if (cipher.empty() || sessionKey.data.empty()) {
            return std::unexpected(ErrorCode::BadIntegrity);
        }
        const auto now = std::chrono::system_clock::now();
        return Authenticator{
            .cname = "alice@EXAMPLE.ORG",
            .crealm = "EXAMPLE.ORG",
            .ctime = now - std::chrono::seconds(2),
            .cusec = 450123,
            .seqNumber = 1001,
            .subKey = std::nullopt
        };
    }

    KeyBlock serviceKey_;
    ReplayCache replayCache_;
};

} // namespace krb5

int main() {
    using namespace krb5;

    KeyBlock serverKey{ .keyType = 18, .data = std::vector<uint8_t>(32, 0x5F) };
    ServerValidator validator(std::move(serverKey));

    std::vector<uint8_t> dummyTicket(128, 1);
    std::vector<uint8_t> dummyAuth(64, 2);

    auto result1 = validator.verifyApReq(dummyTicket, dummyAuth);
    if (result1) {
        std::cout << "Спроба 1: УСПІШНО автентифіковано. Розмір сесійного ключа: "
                  << result1->data.size() << " байтів\n";
    } else {
        std::cout << "Спроба 1: помилка " << static_cast<int>(result1.error()) << "\n";
    }

    auto result2 = validator.verifyApReq(dummyTicket, dummyAuth);
    if (!result2 && result2.error() == ErrorCode::RepeatDetected) {
        std::cout << "Спроба 2: УСПІШНО заблоковано повтор (Replay Attack Detected, код 34)\n";
    } else {
        std::cout << "Спроба 2: несподіваний результат!\n";
    }

    return 0;
}
