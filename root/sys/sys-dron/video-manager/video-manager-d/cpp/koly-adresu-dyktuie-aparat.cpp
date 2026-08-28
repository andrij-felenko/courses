switch (pInfo->type()) {
case VIDEO_STREAM_TYPE_RTSP:
    source = VideoSettings::videoSourceRTSP;
    url = pInfo->uri();
    break;
case VIDEO_STREAM_TYPE_RTPUDP:
    if (pInfo->encoding() == VIDEO_STREAM_ENCODING_H265) {
        source = VideoSettings::videoSourceUDPH265;
        url = pInfo->uri().contains("udp265://") ? pInfo->uri() : QStringLiteral("udp265://0.0.0.0:%1").arg(pInfo->uri());
    } else {
        source = VideoSettings::videoSourceUDPH264;
        url = pInfo->uri().contains("udp://") ? pInfo->uri() : QStringLiteral("udp://0.0.0.0:%1").arg(pInfo->uri());
    }
    break;
