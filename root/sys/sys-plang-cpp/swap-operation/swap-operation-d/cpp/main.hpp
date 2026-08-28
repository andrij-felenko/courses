namespace geo {

class Path {
public:
    void swap(Path& other) noexcept {
        points_.swap(other.points_);
        std::swap(closed_, other.closed_);
    }
    friend void swap(Path& a, Path& b) noexcept { a.swap(b); }

private:
    std::vector<Point> points_;
    bool closed_ = false;
};

}  // namespace geo
