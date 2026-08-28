#include <iostream>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <cstdint>
#include <algorithm>

namespace aries {

using LSN = uint64_t;
using XID = uint32_t;

enum class LogType {
    Update,
    Commit,
    Abort,
    CLR
};

struct WalRecord {
    LSN lsn{0};
    LSN prev_lsn{0};
    LSN undo_next_lsn{0};
    XID xid{0};
    LogType type{LogType::Update};
    uint32_t page_id{0};
    int32_t old_val{0};
    int32_t new_val{0};
};

struct Page {
    uint32_t page_id{0};
    LSN page_lsn{0};
    int32_t data{0};
};

class WalEngine {
public:
    WalEngine() : next_lsn_(100), flushed_lsn_(0) {
        for (uint32_t i = 0; i < 16; ++i) {
            pages_[i] = Page{i, 0, 0};
        }
    }

    LSN append_record(XID xid, LogType type, uint32_t page_id, int32_t old_v, int32_t new_v, LSN undo_next = 0) {
        LSN lsn = next_lsn_++;
        WalRecord rec;
        rec.lsn = lsn;
        rec.prev_lsn = last_tx_lsn_[xid];
        rec.undo_next_lsn = undo_next;
        rec.xid = xid;
        rec.type = type;
        rec.page_id = page_id;
        rec.old_val = old_v;
        rec.new_val = new_v;

        log_.push_back(rec);
        last_tx_lsn_[xid] = lsn;
        return lsn;
    }

    void update_page(XID xid, uint32_t page_id, int32_t new_val) {
        int32_t old_val = pages_[page_id].data;
        LSN lsn = append_record(xid, LogType::Update, page_id, old_val, new_val);
        pages_[page_id].data = new_val;
        pages_[page_id].page_lsn = lsn;
    }

    void commit(XID xid) {
        LSN commit_lsn = append_record(xid, LogType::Commit, 0, 0, 0);
        flushed_lsn_ = std::max(flushed_lsn_, commit_lsn);
    }

    void recover() {
        std::cout << "=== Старт ARIES відновлення (C++) ===" << std::endl;

        // 1. Фаза аналізу
        std::unordered_set<XID> active_tx;
        std::unordered_map<XID, LSN> last_active_lsn;

        for (const auto& rec : log_) {
            if (rec.type == LogType::Update || rec.type == LogType::CLR) {
                active_tx.insert(rec.xid);
                last_active_lsn[rec.xid] = rec.lsn;
            } else if (rec.type == LogType::Commit || rec.type == LogType::Abort) {
                active_tx.erase(rec.xid);
            }
        }

        // 2. Фаза Redo
        for (const auto& rec : log_) {
            if (rec.type == LogType::Update || rec.type == LogType::CLR) {
                auto& p = pages_[rec.page_id];
                if (rec.lsn > p.page_lsn) {
                    p.data = rec.new_val;
                    p.page_lsn = rec.lsn;
                }
            }
        }

        // 3. Фаза Undo
        for (XID xid : active_tx) {
            LSN curr_lsn = last_active_lsn[xid];
            while (curr_lsn > 0) {
                auto it = std::find_if(log_.begin(), log_.end(), [curr_lsn](const WalRecord& r) {
                    return r.lsn == curr_lsn;
                });
                if (it == log_.end()) break;

                if (it->type == LogType::Update) {
                    LSN clr_lsn = append_record(it->xid, LogType::CLR, it->page_id, it->new_val, it->old_val, it->prev_lsn);
                    auto& p = pages_[it->page_id];
                    p.data = it->old_val;
                    p.page_lsn = clr_lsn;
                    curr_lsn = it->prev_lsn;
                } else if (it->type == LogType::CLR) {
                    curr_lsn = it->undo_next_lsn;
                } else {
                    curr_lsn = it->prev_lsn;
                }
            }
            append_record(xid, LogType::Abort, 0, 0, 0);
        }
        std::cout << "=== Відновлення успішно завершено ===" << std::endl;
    }

private:
    LSN next_lsn_{100};
    LSN flushed_lsn_{0};
    std::vector<WalRecord> log_;
    std::unordered_map<uint32_t, Page> pages_;
    std::unordered_map<XID, LSN> last_tx_lsn_;
};

} // namespace aries
