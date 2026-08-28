namespace physics::mechanics {

class MpiGridDistributor {
public:
    static void distributeGrid(const Config& config,
                               size_t grid_width,
                               size_t grid_height,
                               int rank,
                               int world_size) noexcept {}
};

}
