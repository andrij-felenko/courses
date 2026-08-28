#include <cstdint>
#include <span>
#include <vector>
#include <memory>
#include <optional>

/* Ідіоматична C++ обгортка над внутрішніми структурами GiST */
struct GistEntryView {
    uintptr_t raw_key{0};
    uint32_t page_id{0};
    uint16_t offset{0};
    bool is_leaf{false};
    bool is_null{false};
};

struct GistSplitResult {
    std::vector<uint16_t> left_offsets;
    uintptr_t left_union_key{0};

    std::vector<uint16_t> right_offsets;
    uintptr_t right_union_key{0};
};

class IGistOperatorClass {
public:
    virtual ~IGistOperatorClass() = default;

    [[nodiscard]] virtual bool consistent(const GistEntryView& entry,
                                          uintptr_t query,
                                          uint16_t strategy,
                                          bool& out_recheck) const = 0;

    [[nodiscard]] virtual uintptr_t compute_union(std::span<const GistEntryView> entries) const = 0;

    [[nodiscard]] virtual float penalty(const GistEntryView& orig_entry,
                                        const GistEntryView& new_entry) const = 0;

    [[nodiscard]] virtual GistSplitResult pick_split(std::span<const GistEntryView> entries) const = 0;

    [[nodiscard]] virtual bool equal(uintptr_t key_a, uintptr_t key_b) const = 0;
};
