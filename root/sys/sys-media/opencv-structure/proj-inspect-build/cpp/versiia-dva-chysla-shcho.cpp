#include <opencv2/core.hpp>
#include <opencv2/core/ocl.hpp>
#include <opencv2/core/utility.hpp>
#include <opencv2/core/version.hpp>
#include <opencv2/core/utils/logger.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/videoio/registry.hpp>

#include <algorithm>
#include <cstdio>
#include <functional>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

namespace reg = cv::videoio_registry;

// CV_VERSION_* прийшли із заголовків, які бачив КОМПІЛЯТОР;
// getVersion*() виконується всередині тієї libopencv_core,
// яку підставив ЗАВАНТАЖУВАЧ. Це два незалежні числа.
static bool headerMatchesLibrary()
{
    return cv::getVersionMajor()    == CV_VERSION_MAJOR
        && cv::getVersionMinor()    == CV_VERSION_MINOR
        && cv::getVersionRevision() == CV_VERSION_REVISION;
}

static void reportVersion()
{
    std::cout << "OpenCV\n"
              << "  бібліотека: " << cv::getVersionString() << "\n"
              << "  заголовки:  " << CV_VERSION << "\n";
    if (!headerMatchesLibrary())
        std::cout << "  ! заголовки й бібліотека з різних збірок\n";
}
