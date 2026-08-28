struct Set {
    uint32_t id = 0;
    std::vector<uint64_t> elements;
};

struct Signature {
    uint32_t id = 0;
    std::vector<uint64_t> sig;
};

struct Match {
    uint32_t id_a = 0;
    uint32_t id_b = 0;
    double similarity = 0.0;
};
