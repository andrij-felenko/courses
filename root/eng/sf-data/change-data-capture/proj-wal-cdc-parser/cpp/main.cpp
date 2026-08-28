#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <unordered_map>
#include <memory>
#include <span>
#include <cstdint>
#include <cstring>
#include <format>
#include <optional>

enum class RecordType : uint8_t {
    Begin  = 0x01,
    Insert = 0x02,
    Update = 0x03,
    Delete = 0x04,
    Commit = 0x05,
    Abort  = 0x06
};

struct ChangeRecord {
    RecordType  type;
    uint64_t    lsn;
    uint64_t    xid;
    uint32_t    table_id;
    uint64_t    pk;
    std::string before_data;
    std::string after_data;
};

struct TxState {
    uint64_t xid;
    uint64_t begin_lsn;
    uint64_t begin_ts;
    std::vector<ChangeRecord> records;
};

class CdcEngine {
public:
    explicit CdcEngine(size_t reserve_tx = 1024) {
        active_transactions_.reserve(reserve_tx);
    }

    bool process_record(std::span<const uint8_t> buffer) {
        if (buffer.size() < 21) return false;

        const auto type = static_cast<RecordType>(buffer[0]);
        uint32_t length = 0;
        uint64_t lsn = 0;
        uint64_t xid = 0;

        std::memcpy(&length, buffer.data() + 1, sizeof(length));
        std::memcpy(&lsn, buffer.data() + 5, sizeof(lsn));
        std::memcpy(&xid, buffer.data() + 13, sizeof(xid));

        if (buffer.size() < length) return false;
        auto payload = buffer.subspan(21, length - 21);

        switch (type) {
            case RecordType::Begin: {
                uint64_t ts = 0;
                if (payload.size() >= sizeof(ts)) {
                    std::memcpy(&ts, payload.data(), sizeof(ts));
                }
                active_transactions_[xid] = TxState{
                    .xid = xid,
                    .begin_lsn = lsn,
                    .begin_ts = ts,
                    .records = {}
                };
                return true;
            }

            case RecordType::Abort: {
                active_transactions_.erase(xid);
                return true;
            }

            case RecordType::Commit: {
                auto it = active_transactions_.find(xid);
                if (it == active_transactions_.end()) return false;

                uint64_t commit_lsn = 0;
                uint64_t commit_ts = 0;
                if (payload.size() >= 16) {
                    std::memcpy(&commit_lsn, payload.data(), sizeof(commit_lsn));
                    std::memcpy(&commit_ts, payload.data() + 8, sizeof(commit_ts));
                }

                for (const auto &rec : it->second.records) {
                    emit_event(rec, commit_lsn, commit_ts);
                }

                last_confirmed_lsn_ = commit_lsn;
                active_transactions_.erase(it);
                return true;
            }

            case RecordType::Insert:
            case RecordType::Update:
            case RecordType::Delete: {
                auto it = active_transactions_.find(xid);
                if (it == active_transactions_.end()) return false;

                if (payload.size() < 12) return false;
                uint32_t table_id = 0;
                uint64_t pk = 0;
                std::memcpy(&table_id, payload.data(), sizeof(table_id));
                std::memcpy(&pk, payload.data() + 4, sizeof(pk));

                ChangeRecord rec{
                    .type = type,
                    .lsn = lsn,
                    .xid = xid,
                    .table_id = table_id,
                    .pk = pk,
                    .before_data = {},
                    .after_data = {}
                };

                if (type == RecordType::Insert) {
                    uint32_t dlen = 0;
                    std::memcpy(&dlen, payload.data() + 12, sizeof(dlen));
                    if (payload.size() >= 16 + dlen) {
                        rec.after_data.assign(reinterpret_cast<const char*>(payload.data() + 16), dlen);
                    }
                } else if (type == RecordType::Update) {
                    uint32_t old_len = 0;
                    std::memcpy(&old_len, payload.data() + 12, sizeof(old_len));
                    if (payload.size() >= 16 + old_len + 4) {
                        rec.before_data.assign(reinterpret_cast<const char*>(payload.data() + 16), old_len);
                        uint32_t new_len = 0;
                        std::memcpy(&new_len, payload.data() + 16 + old_len, sizeof(new_len));
                        if (payload.size() >= 20 + old_len + new_len) {
                            rec.after_data.assign(reinterpret_cast<const char*>(payload.data() + 20 + old_len), new_len);
                        }
                    }
                } else if (type == RecordType::Delete) {
                    uint32_t old_len = 0;
                    std::memcpy(&old_len, payload.data() + 12, sizeof(old_len));
                    if (payload.size() >= 16 + old_len) {
                        rec.before_data.assign(reinterpret_cast<const char*>(payload.data() + 16), old_len);
                    }
                }

                it->second.records.push_back(std::move(rec));
                return true;
            }
        }
        return false;
    }

    [[nodiscard]] uint64_t confirmed_flush_lsn() const noexcept {
        return last_confirmed_lsn_;
    }

private:
    void emit_event(const ChangeRecord &rec, uint64_t commit_lsn, uint64_t commit_ts) const {
        std::string_view op = "u";
        if (rec.type == RecordType::Insert) op = "c";
        else if (rec.type == RecordType::Delete) op = "d";

        std::string before_val = rec.before_data.empty() ? "null" : std::format("\"{}\"", rec.before_data);
        std::string after_val = rec.after_data.empty() ? "null" : std::format("\"{}\"", rec.after_data);

        std::cout << std::format(
            "{{\"op\":\"{}\",\"lsn\":{},\"commit_lsn\":{},\"xid\":{},\"table_id\":{},\"pk\":{},\"ts\":{},\"before\":{},\"after\":{}}}\n",
            op, rec.lsn, commit_lsn, rec.xid, rec.table_id, rec.pk, commit_ts, before_val, after_val
        );
    }

    std::unordered_map<uint64_t, TxState> active_transactions_;
    uint64_t last_confirmed_lsn_ = 0;
};
