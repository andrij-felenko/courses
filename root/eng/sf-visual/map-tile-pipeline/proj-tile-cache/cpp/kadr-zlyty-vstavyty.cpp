struct Ready {
    TileId    id;
    RasterPtr raster;
    uint64_t  generation;
};

class ReadyQueue {
public:
    void publish(Ready r) {
        std::lock_guard<std::mutex> lock(m_);
        q_.push_back(std::move(r));
    }
    // Забрати все одним обміном. Викликач подає ПОРОЖНІЙ вектор:
    // буфери просто міняються місцями, і після розігріву ніхто не алокує.
    void drain(std::vector<Ready>& out) {
        std::lock_guard<std::mutex> lock(m_);
        out.swap(q_);
        q_.clear();
    }
private:
    std::mutex m_;
    std::vector<Ready> q_;
};
