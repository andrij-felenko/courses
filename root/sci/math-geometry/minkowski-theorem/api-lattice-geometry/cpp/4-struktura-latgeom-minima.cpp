namespace latgeom {

struct MinimaVerification {
    std::vector<double> lambda;
    double product_lambda{0.0};
    double lower_bound{0.0};
    double upper_bound{0.0};
    bool satisfies_second_theorem{false};
};

} // namespace latgeom
