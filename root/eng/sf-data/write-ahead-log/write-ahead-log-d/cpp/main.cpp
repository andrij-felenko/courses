#include <vector>
#include <iostream>
#include <cstdint>

using LSN = uint64_t;

struct WalRecord {
    LSN lsn{0};
    LSN prev_lsn{0};
    LSN undo_next_lsn{0};
    uint32_t xid{0};
    uint32_t page_id{0};
    int32_t new_val{0};
};

void aries_redo_scan(const std::vector<WalRecord>& log, std::vector<int32_t>& pages, std::vector<LSN>& page_lsns) {
    for (const auto& rec : log) {
        if (rec.lsn > page_lsns[rec.page_id]) {
            pages[rec.page_id] = rec.new_val;
            page_lsns[rec.page_id] = rec.lsn;
            std::cout << "Redo: застосовано LSN " << rec.lsn << " до сторінки " << rec.page_id << "\n";
        }
    }
}
