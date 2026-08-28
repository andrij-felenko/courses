// У C++ бітові макроси мапуються на виклики std::vector або std::span:
class DenseGraphBuffer {
public:
    DenseGraphBuffer(size_t n) : n_(n), m_(SETWORDSNEEDED(n)), data_(n * m_, 0) {}

    void add_edge(size_t u, size_t v) {
        ADDONEEDGE(data_.data(), u, v, m_);
    }

    bool has_edge(size_t u, size_t v) const {
        return ISELEMENT(GRAPHROW(data_.data(), u, m_), v);
    }

    graph* data() { return data_.data(); }
    int m() const { return m_; }
    int n() const { return static_cast<int>(n_); }

private:
    size_t n_;
    int m_;
    std::vector<graph> data_;
};
