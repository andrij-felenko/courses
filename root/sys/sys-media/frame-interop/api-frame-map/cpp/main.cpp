// Кадр із конвеєра → BGR. Заголовки над площинами нічого не копіюють;
// копія відбувається лише всередині cvtColor і merge, де без неї не обійтися.
static bool frame_to_bgr(const GstVideoFrame& f, cv::Mat& bgr)
{
    const int w = GST_VIDEO_FRAME_WIDTH(&f);
    const int h = GST_VIDEO_FRAME_HEIGHT(&f);
    const int cw = GST_VIDEO_FRAME_COMP_WIDTH(&f, 1);    // ширина хроми
    const int ch = GST_VIDEO_FRAME_COMP_HEIGHT(&f, 1);   // висота хроми

    switch (GST_VIDEO_FRAME_FORMAT(&f)) {

    case GST_VIDEO_FORMAT_BGR: {
        cv::Mat src(h, w, CV_8UC3, GST_VIDEO_FRAME_PLANE_DATA(&f, 0),
                                   GST_VIDEO_FRAME_PLANE_STRIDE(&f, 0));
        src.copyTo(bgr);            // без copyTo це позика, що помре на unmap
        return true;
    }
    case GST_VIDEO_FORMAT_BGRx:
    case GST_VIDEO_FORMAT_BGRA: {
        cv::Mat src(h, w, CV_8UC4, GST_VIDEO_FRAME_PLANE_DATA(&f, 0),
                                   GST_VIDEO_FRAME_PLANE_STRIDE(&f, 0));
        cv::cvtColor(src, bgr, cv::COLOR_BGRA2BGR);
        return true;
    }
    case GST_VIDEO_FORMAT_GRAY8: {
        cv::Mat src(h, w, CV_8UC1, GST_VIDEO_FRAME_PLANE_DATA(&f, 0),
                                   GST_VIDEO_FRAME_PLANE_STRIDE(&f, 0));
        cv::cvtColor(src, bgr, cv::COLOR_GRAY2BGR);
        return true;
    }
    case GST_VIDEO_FORMAT_YUY2: {
        cv::Mat src(h, w, CV_8UC2, GST_VIDEO_FRAME_PLANE_DATA(&f, 0),
                                   GST_VIDEO_FRAME_PLANE_STRIDE(&f, 0));
        cv::cvtColor(src, bgr, cv::COLOR_YUV2BGR_YUY2);
        return true;
    }
    case GST_VIDEO_FORMAT_NV12:
    case GST_VIDEO_FORMAT_NV21: {
        cv::Mat y (h,  w,  CV_8UC1, GST_VIDEO_FRAME_PLANE_DATA(&f, 0),
                                    GST_VIDEO_FRAME_PLANE_STRIDE(&f, 0));
        cv::Mat uv(ch, cw, CV_8UC2, GST_VIDEO_FRAME_PLANE_DATA(&f, 1),
                                    GST_VIDEO_FRAME_PLANE_STRIDE(&f, 1));
        cv::cvtColorTwoPlane(y, uv, bgr,
            GST_VIDEO_FRAME_FORMAT(&f) == GST_VIDEO_FORMAT_NV12
                ? cv::COLOR_YUV2BGR_NV12 : cv::COLOR_YUV2BGR_NV21);
        return true;
    }
    case GST_VIDEO_FORMAT_I420:
    case GST_VIDEO_FORMAT_YV12: {
        // COMP, а не PLANE: компонента 1 — завжди U, компонента 2 — завжди V,
        // тому обидва формати проходять цією гілкою без розрізнення.
        cv::Mat y(h,  w,  CV_8UC1, GST_VIDEO_FRAME_COMP_DATA(&f, 0),
                                   GST_VIDEO_FRAME_COMP_STRIDE(&f, 0));
        cv::Mat u(ch, cw, CV_8UC1, GST_VIDEO_FRAME_COMP_DATA(&f, 1),
                                   GST_VIDEO_FRAME_COMP_STRIDE(&f, 1));
        cv::Mat v(ch, cw, CV_8UC1, GST_VIDEO_FRAME_COMP_DATA(&f, 2),
                                   GST_VIDEO_FRAME_COMP_STRIDE(&f, 2));
        cv::Mat uv;
        cv::merge(std::vector<cv::Mat>{u, v}, uv);   // U та V поруч — розкладка NV12
        cv::cvtColorTwoPlane(y, uv, bgr, cv::COLOR_YUV2BGR_NV12);
        return true;
    }
    default:
        return false;               // формат не з нашого списку — хай його візьме videoconvert
    }
}
