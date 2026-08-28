#include <vector>

struct SubdividedPath {
    std::size_t u;
    std::size_t v;
    std::vector<std::size_t> vertices;
};

struct KuratowskiWitness {
    ObstructionType type{ObstructionType::None};
    std::vector<std::size_t> core_vertices;
    std::vector<SubdividedPath> paths;

    [[nodiscard]] bool is_valid() const noexcept {
        return type != ObstructionType::None;
    }
};
