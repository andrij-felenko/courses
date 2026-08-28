#include <string_view>
#include <span>
#include <expected>

class IResourceManager {
public:
    virtual ~IResourceManager() = default;

    virtual std::expected<void, int> open(std::string_view info, int rm_id, int64_t flags) = 0;
    virtual std::expected<void, int> close(std::string_view info, int rm_id, int64_t flags) = 0;
    virtual std::expected<void, int> start(const TransactionId& xid, int rm_id, int64_t flags) = 0;
    virtual std::expected<void, int> end(const TransactionId& xid, int rm_id, int64_t flags) = 0;
    virtual std::expected<int, int> prepare(const TransactionId& xid, int rm_id, int64_t flags) = 0;
    virtual std::expected<void, int> commit(const TransactionId& xid, int rm_id, int64_t flags) = 0;
    virtual std::expected<void, int> rollback(const TransactionId& xid, int rm_id, int64_t flags) = 0;
    virtual std::expected<size_t, int> recover(std::span<TransactionId> xids, int rm_id, int64_t flags) = 0;
    virtual std::expected<void, int> forget(const TransactionId& xid, int rm_id, int64_t flags) = 0;
};
