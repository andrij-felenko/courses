int main(void) {
    const Point raw[] = {
        {0.0, 0.0}, {1.0, 0.1}, {2.0, -0.1}, {3.0, 5.0},
        {4.0, 5.2}, {5.0, 0.0}, {6.0, 0.2},  {7.0, 0.0}
    };
    size_t n = sizeof(raw) / sizeof(raw[0]);
    double eps = 1.0;

    bool keep[8];
    size_t rdp_count = douglas_peucker_iterative(raw, n, eps, keep);
    printf("Douglas-Peucker: %zu точок з %zu збережено (eps=1.0)\n", rdp_count, n);

    Point rw_out[8];
    size_t rw_count = simplify_reumann_witkam(raw, n, eps, rw_out);
    printf("Reumann-Witkam:  %zu точок з %zu збережено (eps=1.0)\n", rw_count, n);

    Point vw_out[8];
    size_t vw_count = simplify_visvalingam_whyatt(raw, n, 4, vw_out);
    printf("Visvalingam:     %zu точок збережено (target=4)\n", vw_count);

    return 0;
}
