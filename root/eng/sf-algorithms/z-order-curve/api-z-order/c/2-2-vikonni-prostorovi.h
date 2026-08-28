size_t morton_range_query2d(
    const Point2D *points,
    size_t count,
    const morton_box2d_t *box,
    Point2D *out_results,
    size_t max_results
);

void morton_bigmin_litmax2d(
    uint64_t curr_z,
    const morton_box2d_t *box,
    uint64_t *out_bigmin,
    uint64_t *out_litmax
);
