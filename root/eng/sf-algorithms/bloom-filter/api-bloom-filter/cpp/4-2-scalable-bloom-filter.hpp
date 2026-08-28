#include <vector>
#include <cstddef>
#include <string_view>

namespace sys {

class scalable_bloom_filter {
public:
    explicit scalable_bloom_filter(double target_fp_rate);
    void add(std::string_view key);
    [[nodiscard]] bool contains(std::string_view key) const noexcept;

private:
    std::vector<bloom_filter> layers_;
    double target_fp_;
};

} // namespace sys
