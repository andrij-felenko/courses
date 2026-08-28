// Забирає володіння зразком. Порожній Mat означає «кадр не придатний».
cv::Mat matFromSample(GstSample* sample, FrameFormat& ff)
{
    SamplePtr guard(sample);                     // поки що зразок наш
    GstCaps*   caps = gst_sample_get_caps(sample);
    GstBuffer* buf  = gst_sample_get_buffer(sample);
    if (!caps || !buf || !refreshFormat(ff, caps))
        return {};

    auto hold = std::make_unique<MappedSample>();
    if (!gst_buffer_map(buf, &hold->map, GST_MAP_READ))
        return {};

    const int    h      = GST_VIDEO_INFO_HEIGHT(&ff.info);
    const int    w      = GST_VIDEO_INFO_WIDTH(&ff.info);
    const size_t stride = (size_t) GST_VIDEO_INFO_PLANE_STRIDE(&ff.info, 0);
    if (hold->map.size < stride * (size_t) h) {
        gst_buffer_unmap(buf, &hold->map);
        return {};
    }

    cv::Mat m(h, w, ff.cvType, hold->map.data, stride);   // заголовок без володіння…

    int    sizes[2] = { h, w };
    size_t steps[2] = { stride, CV_ELEM_SIZE(ff.cvType) };
    m.u = gstAllocator().allocate(2, sizes, ff.cvType, hold->map.data, steps,
                                  cv::ACCESS_RW, cv::USAGE_DEFAULT);

    hold->sample  = guard.release();   // з цієї миті зразок належить кадрові
    hold->buffer  = buf;
    m.u->userdata = hold.release();
    m.addref();                        // refcount 0 → 1: цей заголовок — перший власник

    return m;                          // …і ось він уже володіє: копіюйте, кладіть у чергу
}
