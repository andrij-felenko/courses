struct Report {
    std::string name;
    double enqueue = 0, compute = 0, deliver = 0, total = 0;
    Wall wall;
    cv::Mat result;
};

static double median(std::vector<double> v)
{
    if (v.empty()) return 0.0;
    std::sort(v.begin(), v.end());
    return v[v.size() / 2];
}

static Report bench(const std::string& name, Route route, bool onDevice,
                    const std::vector<cv::Mat>& frames, int warmup, int measured)
{
    Report r; r.name = name;
    std::vector<double> enq, cmp, dlv, tot;
    cv::Mat  mout;
    cv::UMat uout;

    for (int i = 0; i < warmup + measured; ++i) {
        const cv::Mat& in = frames[i % frames.size()];
        Wall w;

        syncDevice();                    // чужий хвіст у наше число не потрапить
        int64_t t0 = cv::getTickCount();

        if (onDevice) route(in, uout, w);
        else          route(in, mout, w);
        int64_t t1 = cv::getTickCount();   // усе поставлено в чергу; робота ще триває

        syncDevice();
        int64_t t2 = cv::getTickCount();   // а тепер точно скінчилася

        if (onDevice) download(uout, mout, w);   // доставка результату хостові
        int64_t t3 = cv::getTickCount();

        if (i >= warmup) {
            enq.push_back(msBetween(t0, t1));
            cmp.push_back(msBetween(t1, t2));
            dlv.push_back(msBetween(t2, t3));
            tot.push_back(msBetween(t0, t3));
            r.wall = w;
        }
    }

    r.enqueue = median(enq);  r.compute = median(cmp);
    r.deliver = median(dlv);  r.total   = median(tot);
    mout.copyTo(r.result);
    return r;
}
