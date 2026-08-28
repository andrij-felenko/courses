typedef struct {
    size_t delay_tau;
    size_t dimension_d;
} HorseshoeTakensConfig;

HorseshoeStatus horseshoe_embed_time_series(const double* series,
                                            size_t series_len,
                                            HorseshoeTakensConfig cfg,
                                            HorseshoePoint2D* out_points,
                                            size_t* out_len);
