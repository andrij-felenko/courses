struct Need {
    std::string           what;   // чого потребує застосунок
    std::function<bool()> probe;  // як це перевірити тут і тепер
    std::string           fix;    // що робити, якщо не склалося
};

static bool listed(const std::vector<cv::VideoCaptureAPIs>& list,
                   cv::VideoCaptureAPIs api)
{
    return std::find(list.begin(), list.end(), api) != list.end();
}

// Найтвердіший доказ: справді відкрити крихітний файл потрібним кодеком.
static bool writerWorks(int fourcc)
{
    const std::string probe = cv::tempfile(".mp4");
    cv::VideoWriter w(probe, cv::CAP_FFMPEG, fourcc, 25.0, cv::Size(64, 64));
    const bool ok = w.isOpened();
    w.release();
    std::remove(probe.c_str());
    return ok;
}
