#include <vector>

struct Digest {
    uint64_t sender_id{0};
    uint64_t low_watermark{0};
    uint64_t received_mask{0};
};

std::vector<uint64_t> calculate_missing_sequences(const PbcastReceiver& receiver, 
                                                  const Digest& remote_digest,
                                                  size_t max_requests = 16) {
    std::vector<uint64_t> missing;
    missing.reserve(max_requests);

    const uint64_t local_wm = receiver.low_watermark();
    const uint64_t local_mask = receiver.received_mask();

    /* Перевірка діапазону від local_wm до remote_watermark */
    if (remote_digest.low_watermark > local_wm) {
        for (uint64_t seq = local_wm + 1; seq <= remote_digest.low_watermark; ++seq) {
            const uint64_t offset = seq - local_wm - 1;
            const bool has = (offset < MaskBits) && ((local_mask & (1ULL << offset)) != 0);
            if (!has) {
                missing.push_back(seq);
                if (missing.size() >= max_requests) return missing;
            }
        }
    }

    /* Перевірка бітів у віддаленій масці */
    for (size_t bit = 0; bit < MaskBits; ++bit) {
        if (remote_digest.received_mask & (1ULL << bit)) {
            const uint64_t seq = remote_digest.low_watermark + 1 + bit;
            if (seq > local_wm) {
                const uint64_t offset = seq - local_wm - 1;
                const bool has = (offset < MaskBits) && ((local_mask & (1ULL << offset)) != 0);
                if (!has) {
                    missing.push_back(seq);
                    if (missing.size() >= max_requests) return missing;
                }
            }
        }
    }

    return missing;
}
