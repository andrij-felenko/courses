static void localRangeBody(const cv::Mat& src, cv::Mat& dst, const cv::Mat& mask,
                           int ksize, cv::Mat& scratch)
{
    const int r = ksize / 2, H = src.rows, W = src.cols;

    // Канал 0 — максимум по рядку, канал 1 — мінімум. Один буфер замість двох.
    scratch.create(H, W, CV_8UC2);

    for (int y = 0; y < H; ++y) {
        const uchar* s = src.ptr<uchar>(y);
        uchar* h = scratch.ptr<uchar>(y);
        for (int x = 0; x < W; ++x) {
            const int x0 = std::max(x - r, 0), x1 = std::min(x + r, W - 1);
            int lo = 255, hi = 0;
            for (int xx = x0; xx <= x1; ++xx) {
                const int v = s[xx];
                if (v < lo) lo = v;
                if (v > hi) hi = v;
            }
            h[2 * x] = (uchar)hi;  h[2 * x + 1] = (uchar)lo;
        }
    }

    for (int y = 0; y < H; ++y) {
        uchar* d = dst.ptr<uchar>(y);
        const uchar* m = mask.empty() ? nullptr : mask.ptr<uchar>(y);
        const int y0 = std::max(y - r, 0), y1 = std::min(y + r, H - 1);
        for (int x = 0; x < W; ++x) {
            if (m && !m[x]) { d[x] = 0; continue; }
            int lo = 255, hi = 0;
            for (int yy = y0; yy <= y1; ++yy) {
                const uchar* h = scratch.ptr<uchar>(yy);
                if (h[2 * x]     > hi) hi = h[2 * x];
                if (h[2 * x + 1] < lo) lo = h[2 * x + 1];
            }
            d[x] = (uchar)(hi - lo);
        }
    }
}
