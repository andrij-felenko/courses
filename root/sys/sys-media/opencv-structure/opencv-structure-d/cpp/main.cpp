#include <opencv2/videoio.hpp>
#include <opencv2/videoio/registry.hpp>
#include <iostream>

int main() {
    for (auto api : cv::videoio_registry::getStreamBackends()) {
        std::cout << cv::videoio_registry::getBackendName(api)
                  << (cv::videoio_registry::isBackendBuiltIn(api)
                          ? "  вбудований\n" : "  плагін\n");
    }
}
