using Route = void (*)(const cv::Mat& in, cv::OutputArray out, Wall& w);

// 1. Усе на Mat: межі не існує.
static void routeHost(const cv::Mat& in, cv::OutputArray out, Wall&)
{
    cv::Mat gray, blur, curved;
    cv::cvtColor(in, gray, cv::COLOR_BGR2GRAY);
    cv::GaussianBlur(gray, blur, {5, 5}, 1.5);
    curveOnHost(blur, curved);
    cv::threshold(curved, out, 128, 255, cv::THRESH_BINARY);
}

// 2. Усе на UMat: крива — бібліотечним LUT, у якого гілка на пристрої є.
static void routeDevice(const cv::Mat& in, cv::OutputArray out, Wall& w)
{
    cv::UMat uin, gray, blur, curved;
    upload(in, uin, w);                                   // єдиний перетин межі
    cv::cvtColor(uin, gray, cv::COLOR_BGR2GRAY);
    cv::GaussianBlur(gray, blur, {5, 5}, 1.5);
    cv::LUT(blur, g_curveU, curved);
    cv::threshold(curved, out, 128, 255, cv::THRESH_BINARY);
}

// 3. Те саме, але крива — нашим циклом: посеред ланцюжка з'являється межа.
static void routeSplit(const cv::Mat& in, cv::OutputArray out, Wall& w)
{
    cv::UMat uin, gray, blur, curved;
    upload(in, uin, w);
    cv::cvtColor(uin, gray, cv::COLOR_BGR2GRAY);
    cv::GaussianBlur(gray, blur, {5, 5}, 1.5);

    cv::Mat hblur, hcurved;
    download(blur, hblur, w);                             // тут потік зупиняється
    curveOnHost(hblur, hcurved);
    upload(hcurved, curved, w);

    cv::threshold(curved, out, 128, 255, cv::THRESH_BINARY);
}

// 4. Те саме, але крива — власним ядром: межа зникає знову.
static void routeKernel(const cv::Mat& in, cv::OutputArray out, Wall& w)
{
    cv::UMat uin, gray, blur, curved;
    upload(in, uin, w);
    cv::cvtColor(uin, gray, cv::COLOR_BGR2GRAY);
    cv::GaussianBlur(gray, blur, {5, 5}, 1.5);
    if (!curveOnDevice(blur, curved))
        cv::LUT(blur, g_curveU, curved);                  // запасний шлях, якщо ядра немає
    cv::threshold(curved, out, 128, 255, cv::THRESH_BINARY);
}
