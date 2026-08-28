#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <optional>
#include <expected>
#include <iomanip>
#include <sstream>
#include <cstring>
#include <span>

namespace claimcheck {

constexpr size_t THRESHOLD_BYTES = 64 * 1024;

enum class ErrorCode {
    StorageWriteFailed,
    StorageReadFailed,
    IntegrityMismatch,
    AllocationError
};

struct ClaimTicket {
    std::string claim_id;
    bool is_external{false};
    std::string storage_uri;
    std::string content_sha256;
    size_t size_bytes{0};
    std::vector<uint8_t> inline_payload;
};

class BlobStorage {
public:
    virtual ~BlobStorage() = default;
    virtual bool put(std::string_view key, std::span<const uint8_t> data) = 0;
    virtual std::optional<std::vector<uint8_t>> get(std::string_view key) = 0;
};

class MockS3Storage final : public BlobStorage {
public:
    bool put(std::string_view key, std::span<const uint8_t> data) override {
        std::cout << "[S3 C++] PUT '" << key << "' (" << data.size() << " B) -> 200 OK\n";
        return true;
    }

    std::optional<std::vector<uint8_t>> get(std::string_view key) override {
        std::cout << "[S3 C++] GET '" << key << "' -> 200 OK\n";
        return std::vector<uint8_t>(120 * 1024, 0xAB);
    }
};

class Pipeline {
public:
    explicit Pipeline(std::shared_ptr<BlobStorage> storage)
        : storage_(std::move(storage)) {}

    static std::string calculate_sha256(std::span<const uint8_t> data) {
        uint64_t h1 = 0xcbf29ce484222325ULL;
        uint64_t h2 = 0x100000001b3ULL;
        for (size_t i = 0; i < data.size(); ++i) {
            h1 = (h1 ^ data[i]) * 0x100000001b3ULL;
            h2 = (h2 ^ (data[i] + i)) * 0xcbf29ce484222325ULL;
        }
        std::ostringstream ss;
        ss << std::hex << std::setfill('0')
           << std::setw(16) << h1 << std::setw(16) << h2
           << std::setw(16) << (h1 ^ h2) << std::setw(16) << (h1 + h2);
        return ss.str();
    }

    std::expected<ClaimTicket, ErrorCode> produce(std::span<const uint8_t> payload) {
        ClaimTicket ticket;
        ticket.claim_id = "clm-cpp-" + std::to_string(payload.size());
        ticket.size_bytes = payload.size();
        ticket.content_sha256 = calculate_sha256(payload);

        if (payload.size() <= THRESHOLD_BYTES) {
            ticket.is_external = false;
            ticket.inline_payload.assign(payload.begin(), payload.end());
            return ticket;
        }

        ticket.is_external = true;
        ticket.storage_uri = "s3://corporate-events/blobs/" + ticket.content_sha256;

        if (!storage_->put(ticket.storage_uri, payload)) {
            return std::unexpected(ErrorCode::StorageWriteFailed);
        }
        return ticket;
    }

    std::expected<std::vector<uint8_t>, ErrorCode> consume(const ClaimTicket& ticket) {
        if (!ticket.is_external) {
            return ticket.inline_payload;
        }

        auto blob_opt = storage_->get(ticket.storage_uri);
        if (!blob_opt) {
            return std::unexpected(ErrorCode::StorageReadFailed);
        }

        if (calculate_sha256(*blob_opt) != ticket.content_sha256) {
            return std::unexpected(ErrorCode::IntegrityMismatch);
        }
        return *blob_opt;
    }

private:
    std::shared_ptr<BlobStorage> storage_;
};

} // namespace claimcheck
