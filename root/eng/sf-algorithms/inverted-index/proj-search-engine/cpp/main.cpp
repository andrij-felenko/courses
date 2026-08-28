#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <unordered_map>
#include <memory>
#include <cmath>
#include <span>
#include <cstdint>

namespace ir {

constexpr size_t BLOCK_SIZE = 8;

/* --- 1. Побайтовий компресор Varint (VByte) --- */
class VByteCodec {
public:
    static void encode(uint32_t val, std::vector<uint8_t>& dest) {
        while (val >= 0x80) {
            dest.push_back(static_cast<uint8_t>((val & 0x7F) | 0x80));
            val >>= 7;
        }
        dest.push_back(static_cast<uint8_t>(val & 0x7F));
    }

    static uint32_t decode(std::span<const uint8_t>& stream) {
        uint32_t result = 0;
        uint32_t shift = 0;
        size_t bytes_read = 0;

        for (uint8_t byte : stream) {
            bytes_read++;
            result |= static_cast<uint32_t>(byte & 0x7F) << shift;
            if (!(byte & 0x80)) {
                break;
            }
            shift += 7;
        }
        stream = stream.subspan(bytes_read);
        return result;
    }
};

/* --- 2. Постинговий список із блоковими Skip-покажчиками --- */
struct SkipBlock {
    uint32_t max_doc_id;
    size_t byte_offset;
};

class PostingList {
public:
    PostingList() = default;

    void append(uint32_t doc_id, uint32_t tf) {
        if (doc_count_ == 0) {
            cur_block_start_ = 0;
        }

        uint32_t dgap = (doc_count_ == 0) ? doc_id : (doc_id - last_doc_id_);
        last_doc_id_ = doc_id;
        doc_count_++;

        VByteCodec::encode(dgap, data_);
        VByteCodec::encode(tf, data_);

        cur_block_items_++;
        if (cur_block_items_ == BLOCK_SIZE) {
            skips_.push_back({doc_id, cur_block_start_});
            cur_block_items_ = 0;
            cur_block_start_ = data_.size();
        }
    }

    void finalize() {
        if (cur_block_items_ > 0) {
            skips_.push_back({last_doc_id_, cur_block_start_});
            cur_block_items_ = 0;
        }
    }

    [[nodiscard]] const std::vector<uint8_t>& data() const noexcept { return data_; }
    [[nodiscard]] const std::vector<SkipBlock>& skips() const noexcept { return skips_; }
    [[nodiscard]] uint32_t doc_count() const noexcept { return doc_count_; }

private:
    std::vector<uint8_t> data_;
    std::vector<SkipBlock> skips_;
    uint32_t last_doc_id_ = 0;
    uint32_t doc_count_ = 0;
    size_t cur_block_items_ = 0;
    size_t cur_block_start_ = 0;
};

/* --- 3. Стрибковий ітератор (Skip Iterator) --- */
class PostingIterator {
public:
    explicit PostingIterator(const PostingList& pl)
        : pl_(pl), stream_(pl.data()) {
        if (pl_.doc_count() > 0) {
            uint32_t dgap = VByteCodec::decode(stream_);
            current_doc_id_ = dgap;
            current_tf_ = VByteCodec::decode(stream_);
        } else {
            at_end_ = true;
        }
    }

    [[nodiscard]] bool at_end() const noexcept { return at_end_; }
    [[nodiscard]] uint32_t doc_id() const noexcept { return current_doc_id_; }
    [[nodiscard]] uint32_t tf() const noexcept { return current_tf_; }

    void next() {
        if (stream_.empty()) {
            at_end_ = true;
            return;
        }
        uint32_t dgap = VByteCodec::decode(stream_);
        current_doc_id_ += dgap;
        current_tf_ = VByteCodec::decode(stream_);
    }

    void advance(uint32_t target_doc) {
        if (at_end_ || current_doc_id_ >= target_doc) {
            return;
        }

        const auto& skips = pl_.skips();
        while (skip_idx_ + 1 < skips.size() && skips[skip_idx_].max_doc_id < target_doc) {
            skip_idx_++;
            size_t offset = skips[skip_idx_].byte_offset;
            stream_ = std::span<const uint8_t>(pl_.data()).subspan(offset);
            current_doc_id_ = (skip_idx_ > 0) ? skips[skip_idx_ - 1].max_doc_id : 0;
        }

        while (!at_end_ && current_doc_id_ < target_doc) {
            if (stream_.empty()) {
                at_end_ = true;
                break;
            }
            uint32_t dgap = VByteCodec::decode(stream_);
            current_doc_id_ += dgap;
            current_tf_ = VByteCodec::decode(stream_);
        }
    }

private:
    const PostingList& pl_;
    std::span<const uint8_t> stream_;
    size_t skip_idx_ = 0;
    uint32_t current_doc_id_ = 0;
    uint32_t current_tf_ = 0;
    bool at_end_ = false;
};

/* --- 4. Повнотекстовий індекс та ранжування BM25 --- */
struct SearchResult {
    uint32_t doc_id;
    double score;
};

class SearchIndex {
public:
    explicit SearchIndex(uint32_t total_docs, double avg_doc_len)
        : total_docs_(total_docs), avg_doc_len_(avg_doc_len), doc_lengths_(total_docs, 100) {}

    void set_doc_length(uint32_t doc_id, uint32_t len) {
        if (doc_id < doc_lengths_.size()) {
            doc_lengths_[doc_id] = len;
        }
    }

    void add_term_entry(std::string_view term, uint32_t doc_id, uint32_t tf) {
        index_[std::string(term)].append(doc_id, tf);
    }

    void finalize() {
        for (auto& [term, plist] : index_) {
            plist.finalize();
        }
    }

    [[nodiscard]] std::vector<SearchResult> search_and(std::string_view t1, std::string_view t2) const {
        auto it1_entry = index_.find(std::string(t1));
        auto it2_entry = index_.find(std::string(t2));

        if (it1_entry == index_.end() || it2_entry == index_.end()) {
            return {};
        }

        const auto& pl1 = it1_entry->second;
        const auto& pl2 = it2_entry->second;

        PostingIterator it1(pl1);
        PostingIterator it2(pl2);
        std::vector<SearchResult> results;

        while (!it1.at_end() && !it2.at_end()) {
            if (it1.doc_id() == it2.doc_id()) {
                uint32_t did = it1.doc_id();
                uint32_t dlen = doc_lengths_[did];

                double s1 = bm25_score(it1.tf(), dlen, pl1.doc_count());
                double s2 = bm25_score(it2.tf(), dlen, pl2.doc_count());
                results.push_back({did, s1 + s2});

                it1.next();
                it2.next();
            } else if (it1.doc_id() < it2.doc_id()) {
                it1.advance(it2.doc_id());
            } else {
                it2.advance(it1.doc_id());
            }
        }
        return results;
    }

private:
    [[nodiscard]] double bm25_score(uint32_t tf, uint32_t doc_len, uint32_t doc_freq) const noexcept {
        constexpr double k1 = 1.2;
        constexpr double b = 0.75;
        double idf = std::log((static_cast<double>(total_docs_) - doc_freq + 0.5) / (doc_freq + 0.5) + 1.0);
        double b_scale = (1.0 - b) + b * (static_cast<double>(doc_len) / avg_doc_len_);
        double tf_norm = (static_cast<double>(tf) * (k1 + 1.0)) / (static_cast<double>(tf) + k1 * b_scale);
        return idf * tf_norm;
    }

    uint32_t total_docs_;
    double avg_doc_len_;
    std::vector<uint32_t> doc_lengths_;
    std::unordered_map<std::string, PostingList> index_;
};

} // namespace ir

int main() {
    ir::SearchIndex index(100, 150.0);

    for (uint32_t d = 0; d < 100; ++d) {
        index.set_doc_length(d, 100 + (d * 7) % 120);
    }

    index.add_term_entry("алгоритм", 5, 2);
    index.add_term_entry("алгоритм", 18, 1);
    index.add_term_entry("алгоритм", 42, 4);
    index.add_term_entry("алгоритм", 85, 1);

    index.add_term_entry("пошук", 2, 1);
    index.add_term_entry("пошук", 18, 3);
    index.add_term_entry("пошук", 30, 1);
    index.add_term_entry("пошук", 42, 2);
    index.add_term_entry("пошук", 99, 1);

    index.finalize();

    auto matches = index.search_and("алгоритм", "пошук");
    std::cout << "Результати C++ пошуку [ алгоритм AND пошук ]:\n";
    for (const auto& match : matches) {
        std::cout << "  -> DocID: " << match.doc_id
                  << " | BM25 Скор: " << match.score << "\n";
    }

    return 0;
}
