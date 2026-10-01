#include <cstdio>
#include <string>

struct EspBootStatus {
    int rstCause;
    bool gpio15;
    bool gpio0;
    bool gpio2;
};

bool parseRomLog(const std::string& log, EspBootStatus& status) {
    int rawBoot = 0;
    if (sscanf(log.c_str(), "rst cause:%d, bootmode:(%*d,%d)", &status.rstCause, &rawBoot) == 2) {
        status.gpio15 = (rawBoot >> 2) & 1;
        status.gpio0  = (rawBoot >> 1) & 1;
        status.gpio2  = rawBoot & 1;
        return true;
    }
    return false;
}
