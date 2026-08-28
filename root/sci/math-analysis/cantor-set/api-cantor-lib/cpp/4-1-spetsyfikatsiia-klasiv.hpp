namespace math::fractals {

enum class Status {
    Success = 0,
    NullPointer = -1,
    InvalidLevel = -2,
    OutOfBounds = -3,
    MemoryAllocationFailed = -4,
    PrecisionLimitReached = -5
};

class CantorException : public std::runtime_error {
public:
    explicit CantorException(Status status, const std::string& message);
    [[nodiscard]] Status status() const noexcept;
private:
    Status status_;
};

struct AnalysisResult {
    double box_counting_dim{0.0};
    double hausdorff_dim{0.0};
    double mean_squared_error{0.0};
    std::size_t total_boxes_checked{0};
};

class CantorSet {
public:
    explicit CantorSet(std::size_t level = 0);
    ~CantorSet() noexcept = default;

    CantorSet(const CantorSet&) = default;
    CantorSet& operator=(const CantorSet&) = default;
    CantorSet(CantorSet&&) noexcept = default;
    CantorSet& operator=(CantorSet&&) noexcept = default;

    void generate(std::size_t level);
    [[nodiscard]] std::size_t level() const noexcept;
    [[nodiscard]] std::size_t size() const noexcept;
    [[nodiscard]] std::span<const Interval> intervals() const noexcept;

    [[nodiscard]] static bool contains(double x, std::size_t max_depth = 30);
    [[nodiscard]] static double evaluate_staircase(double x, std::size_t depth = 20);

private:
    std::size_t level_{0};
    std::vector<Interval> intervals_;
};

class CantorAnalyzer {
public:
    explicit CantorAnalyzer(CantorSet set);

    [[nodiscard]] AnalysisResult compute_box_counting() const;
    [[nodiscard]] std::vector<double> compute_renyi_spectrum(std::span<const double> q_orders) const;
};

} // namespace math::fractals
