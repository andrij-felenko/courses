struct ImmutableConfig {
    const int port;
    const int max_clients;
};

int benchmark_access(InPlaceOptional<ImmutableConfig>& opt) {
    opt.emplace(ImmutableConfig{8080, 100});
    int p1 = opt->port;

    opt.emplace(ImmutableConfig{9090, 200});
    int p2 = opt->port;

    return p1 + p2;
}
