namespace physics::mechanics {

class VtkExporter {
public:
    static bool exportPolylines(std::span<const Point2D> points, std::string_view filepath) {
        return !points.empty() && !filepath.empty();
    }
};

}
