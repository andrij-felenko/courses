// Кадр іде в appsrc без копіювання пікселів: GstBuffer позичає блок Mat,
// а окремий заголовок на купі тримає цей блок живим, доки буфер не помре.
static void release_mat(gpointer p) { delete static_cast<cv::Mat*>(p); }

GstBuffer* wrap_mat(const cv::Mat& img)
{
    CV_Assert(img.isContinuous());              // інакше розмір ≠ вміст
    const gsize bytes = img.total() * img.elemSize();
    auto* keeper = new cv::Mat(img);            // копія заголовка: +1 до лічильника блока
    return gst_buffer_new_wrapped_full(
        GST_MEMORY_FLAG_READONLY,
        keeper->data, bytes,
        0, bytes,
        keeper, release_mat);
}
