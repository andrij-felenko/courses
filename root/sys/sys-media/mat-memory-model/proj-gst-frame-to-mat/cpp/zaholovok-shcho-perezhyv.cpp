// ✗ так не можна
cv::Mat grab(GstAppSink* sink, FrameFormat& ff) {
    SamplePtr sample(gst_app_sink_pull_sample(sink));
    GstBuffer* buf = gst_sample_get_buffer(sample.get());
    GstMapInfo mi;
    gst_buffer_map(buf, &mi, GST_MAP_READ);

    cv::Mat frame(1080, 1920, CV_8UC3, mi.data);   // заголовок нічого не тримає

    gst_buffer_unmap(buf, &mi);
    return frame;                                   // ← вказівник уже висячий
}
