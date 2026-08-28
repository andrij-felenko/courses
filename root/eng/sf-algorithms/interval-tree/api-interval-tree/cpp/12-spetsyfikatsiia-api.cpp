namespace geo {
    class CenteredIntervalTree {
        double x_mid_;
        std::vector<Interval> intervals_by_low_;
        std::vector<Interval> intervals_by_high_;
        std::unique_ptr<CenteredIntervalTree> left_;
        std::unique_ptr<CenteredIntervalTree> right_;
    public:
        explicit CenteredIntervalTree(std::span<const Interval> intervals);
        [[nodiscard]] std::vector<Interval> query_point(double p) const;
    };
}
