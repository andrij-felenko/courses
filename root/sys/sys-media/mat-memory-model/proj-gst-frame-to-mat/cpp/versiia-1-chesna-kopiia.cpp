// Повертає false, коли потік скінчився або кадр не придатний.
bool pullFrameCopy(GstAppSink* sink, FrameFormat& ff, cv::Mat& out)
{
    GstSample* sample = gst_app_sink_pull_sample(sink);   // наш: transfer full
    if (!sample)
        return false;                                     // EOS або зупинка

    bool ok = false;
    GstBuffer* buf  = gst_sample_get_buffer(sample);      // позичений у зразка
    GstCaps*   caps = gst_sample_get_caps(sample);        // позичений у зразка
    GstMapInfo mi;

    if (buf && caps && refreshFormat(ff, caps) &&
        gst_buffer_map(buf, &mi, GST_MAP_READ))
    {
        const int    h      = GST_VIDEO_INFO_HEIGHT(&ff.info);
        const int    w      = GST_VIDEO_INFO_WIDTH(&ff.info);
        const size_t stride = (size_t) GST_VIDEO_INFO_PLANE_STRIDE(&ff.info, 0);

        if (mi.size >= stride * (size_t) h) {
            cv::Mat view(h, w, ff.cvType, mi.data, stride);  // заголовок без володіння
            view.copyTo(out);                                 // ← єдина копія
            ok = true;
        }
        gst_buffer_unmap(buf, &mi);
    }
    gst_sample_unref(sample);
    return ok;
}
