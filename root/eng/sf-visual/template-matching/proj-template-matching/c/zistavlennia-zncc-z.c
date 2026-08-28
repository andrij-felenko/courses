typedef struct {
    int x;
    int y;
    float sub_x;
    float sub_y;
    double score;
} MatchResult;

typedef struct {
    int w, h;
    double *centered;      // T(u, v) - T_mean
    double sum;            // Σ T
    double var_energy;     // Σ (T - T_mean)^2
    double norm_factor;    // 1.0 / sqrt(var_energy)
} PreparedTemplate;

PreparedTemplate* template_prepare(const uint8_t *tpl, int w, int h, int stride) {
    PreparedTemplate *pt = (PreparedTemplate*)malloc(sizeof(PreparedTemplate));
    if (!pt) return NULL;
    pt->w = w;
    pt->h = h;
    pt->centered = (double*)malloc((size_t)(w * h) * sizeof(double));
    if (!pt->centered) { free(pt); return NULL; }

    double sum = 0.0;
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            sum += (double)tpl[y * stride + x];
        }
    }
    const double mean = sum / (double)(w * h);
    pt->sum = sum;

    double var_energy = 0.0;
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            const double diff = (double)tpl[y * stride + x] - mean;
            pt->centered[y * w + x] = diff;
            var_energy += diff * diff;
        }
    }
    pt->var_energy = var_energy;
    pt->norm_factor = (var_energy > 1e-9) ? (1.0 / sqrt(var_energy)) : 0.0;
    return pt;
}

void template_destroy(PreparedTemplate *pt) {
    if (pt) {
        free(pt->centered);
        free(pt);
    }
}

MatchResult match_zncc_direct(const uint8_t *img, int img_w, int img_h, int img_stride,
                              const PreparedTemplate *tpl, const IntegralImage *ii) {
    MatchResult best = { 0, 0, 0.0f, 0.0f, -2.0 };
    const int max_x = img_w - tpl->w;
    const int max_y = img_h - tpl->h;
    const double area = (double)(tpl->w * tpl->h);

    for (int y = 0; y <= max_y; ++y) {
        for (int x = 0; x <= max_x; ++x) {
            double win_sum = 0.0, win_sqsum = 0.0;
            integral_image_query(ii, x, y, tpl->w, tpl->h, &win_sum, &win_sqsum);
            const double win_var = win_sqsum - (win_sum * win_sum) / area;
            if (win_var < 1e-9) continue;

            const double win_mean = win_sum / area;
            double cross_corr = 0.0;

            for (int ty = 0; ty < tpl->h; ++ty) {
                const uint8_t *i_row = img + (y + ty) * img_stride + x;
                const double *t_row = tpl->centered + ty * tpl->w;
                for (int tx = 0; tx < tpl->w; ++tx) {
                    cross_corr += ((double)i_row[tx] - win_mean) * t_row[tx];
                }
            }

            const double score = cross_corr / (sqrt(win_var) * sqrt(tpl->var_energy));
            if (score > best.score) {
                best.score = score;
                best.x = x;
                best.y = y;
                best.sub_x = (float)x;
                best.sub_y = (float)y;
            }
        }
    }
    return best;
}
