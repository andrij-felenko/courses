namespace geo {
    class IntervalNode {
    public:
        Interval interval;
        double max_high;
        std::unique_ptr<IntervalNode> left;
        std::unique_ptr<IntervalNode> right;

        explicit IntervalNode(Interval it) noexcept;
        void update_max() noexcept;
    };
}
