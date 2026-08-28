#include <vector>
#include <unordered_set>
#include <cstdint>

using TransactionId = uint32_t;

struct Snapshot {
    TransactionId xmin{0};
    TransactionId xmax{0};
    std::unordered_set<TransactionId> active_xids;
};

struct HeapTupleHeader {
    TransactionId t_xmin{0};
    TransactionId t_xmax{0};
    uint16_t t_infomask{0};
};

bool heap_tuple_satisfies_snapshot(const HeapTupleHeader& tuple, const Snapshot& snap, TransactionId current_xid) {
    if (tuple.t_xmin == current_xid) {
        if (tuple.t_xmax == current_xid) return false;
        return true;
    }

    if (tuple.t_xmin >= snap.xmax) return false;
    if (snap.active_xids.count(tuple.t_xmin)) return false;

    if (tuple.t_xmax == 0) return true;
    if (tuple.t_xmax == current_xid) return false;
    if (tuple.t_xmax >= snap.xmax) return true;
    if (snap.active_xids.count(tuple.t_xmax)) return true;

    return false;
}
