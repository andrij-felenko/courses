namespace physics::mechanics {

class CudaAccelerator {
public:
    static void launchKernelBatch(std::span<const Point2D> in_array,
                                  std::span<Point2D> out_array,
                                  const Config& config) noexcept {}
};

}
