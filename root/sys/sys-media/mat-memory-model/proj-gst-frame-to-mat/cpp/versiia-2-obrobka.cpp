// Відображення живе рівно стільки, скільки живе цей об'єкт.
class MappedFrame {
public:
    MappedFrame(GstBuffer* buf, const FrameFormat& ff) : buf_(buf)
    {
        if (!gst_buffer_map(buf_, &mi_, GST_MAP_READ))
            return;
        mapped_ = true;

        const size_t stride = (size_t) GST_VIDEO_INFO_PLANE_STRIDE(&ff.info, 0);
        const int    h      = GST_VIDEO_INFO_HEIGHT(&ff.info);
        if (mi_.size >= stride * (size_t) h)
            mat_ = cv::Mat(h, GST_VIDEO_INFO_WIDTH(&ff.info), ff.cvType, mi_.data, stride);
    }
    ~MappedFrame() { if (mapped_) gst_buffer_unmap(buf_, &mi_); }

    MappedFrame(const MappedFrame&)            = delete;   // відображення не копіюють
    MappedFrame& operator=(const MappedFrame&) = delete;

    bool           ok()  const { return mapped_ && !mat_.empty(); }
    const cv::Mat& mat() const { return mat_; }            // ПОСИЛАННЯ, не копія

private:
    GstBuffer* buf_    = nullptr;
    GstMapInfo mi_{};
    bool       mapped_ = false;
    cv::Mat    mat_;
};

struct SampleDeleter { void operator()(GstSample* s) const { gst_sample_unref(s); } };
using SamplePtr = std::unique_ptr<GstSample, SampleDeleter>;

bool processOneFrame(GstAppSink* sink, FrameFormat& ff)
{
    SamplePtr sample(gst_app_sink_pull_sample(sink));
    if (!sample)
        return false;

    GstBuffer* buf  = gst_sample_get_buffer(sample.get());
    GstCaps*   caps = gst_sample_get_caps(sample.get());
    if (!buf || !caps || !refreshFormat(ff, caps))
        return true;                       // кадр пропускаємо, цикл живе далі

    MappedFrame frame(buf, ff);
    if (frame.ok())
        detect(frame.mat());               // уся робота — тут і тільки тут

    return true;                           // ~MappedFrame → unmap; ~SamplePtr → unref
}
