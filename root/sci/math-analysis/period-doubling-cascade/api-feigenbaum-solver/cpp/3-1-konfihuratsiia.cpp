namespace feigenbaum {

struct Config {
    double r_min = 2.8;
    double r_max = 4.0;
    std::size_t r_steps = 1000;
    std::size_t transient_iters = 1000;
    std::size_t orbit_iters = 500;
};

} // namespace feigenbaum
