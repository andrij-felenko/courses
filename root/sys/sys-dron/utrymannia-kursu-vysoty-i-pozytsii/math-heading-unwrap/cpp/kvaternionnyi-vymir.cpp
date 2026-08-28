struct Quaternion {
    float w{1.0f}, x{0.0f}, y{0.0f}, z{0.0f};

    void ensure_shortest_arc() noexcept {
        if (w < 0.0f) {
            w = -w;
            x = -x;
            y = -y;
            z = -z;
        }
    }
};
