struct TrackInternal {
    std::array<float, 7> state{};
    std::array<float, 49> covariance{};
    int track_id{-1};
    int class_id{0};
    int hits{0};
    int hit_streak{0};
    int age{0};
    int time_since_update{0};
    bool is_active{false};
};
