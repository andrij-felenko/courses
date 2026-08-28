#ifndef DEBRUIJN_GRAPH_HPP
#define DEBRUIJN_GRAPH_HPP

#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <expected>
#include <memory>
#include <cstdint>
#include <span>

namespace dbg {

enum class ErrorCode {
    InvalidKMerLength,
    SequenceContainsInvalidCharacters,
    EmptyGraph,
    GraphNotEulerian,
    BufferTooSmall
};

struct KMer2Bit {
    uint64_t value{0};

    [[nodiscard]] static KMer2Bit from_string(std::string_view sv) noexcept;
    [[nodiscard]] std::string to_string(std::size_t k) const;
    [[nodiscard]] KMer2Bit shift_left(uint8_t next_base, std::size_t k) const noexcept;
    [[nodiscard]] KMer2Bit reverse_complement(std::size_t k) const noexcept;
};

struct NodeState {
    uint8_t out_edges{0};
    uint8_t in_edges{0};
    uint32_t coverage{0};
};

class DeBruijnGraph {
public:
    explicit DeBruijnGraph(std::size_t k);
    ~DeBruijnGraph() = default;

    DeBruijnGraph(const DeBruijnGraph&) = delete;
    DeBruijnGraph& operator=(const DeBruijnGraph&) = delete;

    DeBruijnGraph(DeBruijnGraph&&) noexcept = default;
    DeBruijnGraph& operator=(DeBruijnGraph&&) noexcept = default;

    [[nodiscard]] std::expected<void, ErrorCode> insert_read(std::string_view read_seq);
    [[nodiscard]] std::size_t filter_low_coverage(uint32_t min_coverage);
    [[nodiscard]] std::expected<void, ErrorCode> compact_unitigs();
    [[nodiscard]] std::expected<std::string, ErrorCode> assemble_eulerian_path() const;

    [[nodiscard]] std::size_t node_count() const noexcept { return nodes_.size(); }
    [[nodiscard]] std::size_t k() const noexcept { return k_; }

private:
    std::size_t k_;
    std::unordered_map<uint64_t, NodeState> nodes_;
};

} // namespace dbg

#endif // DEBRUIJN_GRAPH_HPP
