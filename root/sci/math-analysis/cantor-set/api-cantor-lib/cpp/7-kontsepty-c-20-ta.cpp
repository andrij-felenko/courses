template <std::floating_point FloatT>
class GenericCantorSet {
public:
    explicit GenericCantorSet(std::size_t level = 0);
    
    [[nodiscard]] static constexpr bool contains(FloatT x, std::size_t max_depth = 30) noexcept {
        if (x < FloatT{0} || x > FloatT{1}) return false;
        FloatT curr = x;
        for (std::size_t i = 0; i < max_depth; ++i) {
            curr *= FloatT{3};
            const auto digit = static_cast<int>(std::floor(curr));
            if (digit == 1) return false;
            if (digit == 2) curr -= FloatT{2};
        }
        return true;
    }
};
