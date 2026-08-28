namespace feigenbaum {

struct SuperstablePoint {
    double r_superstable = 0.0;
    double residual = 0.0;
    std::size_t iterations = 0;
    double lyapunov = 0.0;
};

} // namespace feigenbaum
