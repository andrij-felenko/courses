struct AppConfig {
    bool readsRtsp   = true;
    bool recordsH264 = true;
    bool usesOpenCL  = false;
};

static std::vector<Need> requirementsOf(const AppConfig& cfg)
{
    std::vector<Need> need;

    need.push_back({
        "заголовки й бібліотека OpenCV з однієї збірки",
        headerMatchesLibrary,
        "у процесі кілька збірок OpenCV; звірте, з чим злінковано плагіни" });

    if (cfg.readsRtsp)
        need.push_back({
            "читання RTSP через GStreamer",
            [] { return listed(reg::getStreamBackends(), cv::CAP_GSTREAMER)
                     && loads(cv::CAP_GSTREAMER); },
            "немає файлу opencv_videoio_gstreamer поруч із бібліотекою "
            "або в теках зі змінної OPENCV_VIDEOIO_PLUGIN_PATH" });

    if (cfg.recordsH264)
        need.push_back({
            "запис H.264 у mp4 через FFmpeg",
            [] { return listed(reg::getWriterBackends(), cv::CAP_FFMPEG)
                     && writerWorks(cv::VideoWriter::fourcc('a','v','c','1')); },
            "бекенд запису є, але кодек avc1 у ньому не піднімається — "
            "перевірте, з якою збіркою FFmpeg зібрано плагін" });

    if (cfg.usesOpenCL)
        need.push_back({
            "OpenCL для cv::UMat",
            [] { return cv::ocl::haveOpenCL() && cv::ocl::useOpenCL(); },
            "рантайму OpenCL немає або його вимкнено; "
            "конвеєр на UMat тихо порахується на процесорі" });

    return need;
}

static bool verify(const std::vector<Need>& needs)
{
    std::vector<const Need*> missing;
    for (const Need& n : needs) {
        bool ok = false;
        try { ok = n.probe(); }
        catch (const cv::Exception&) { ok = false; }
        if (!ok) missing.push_back(&n);
    }
    if (missing.empty()) return true;

    std::cerr << "Ця збірка OpenCV (" << cv::getVersionString()
              << ") не дає застосункові потрібного:\n";
    for (const Need* n : missing)
        std::cerr << "  x " << n->what << "\n      " << n->fix << "\n";
    std::cerr << "Повний перелік здатностей: запустіть із --report.\n";
    return false;
}
