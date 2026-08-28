cv::Mat grabFrame(GstAppSink* sink) {
    GstSample* sample = gst_app_sink_pull_sample(sink);
    GstBuffer* buf = gst_sample_get_buffer(sample);
    GstMapInfo mi;
    gst_buffer_map(buf, &mi, GST_MAP_READ);

    cv::Mat frame(1080, 1920, CV_8UC3, mi.data);   // заголовок без володіння

    gst_buffer_unmap(buf, &mi);
    gst_sample_unref(sample);                       // буфер може бути звільнений
    return frame;                                   // ← покажчик уже висячий
}
