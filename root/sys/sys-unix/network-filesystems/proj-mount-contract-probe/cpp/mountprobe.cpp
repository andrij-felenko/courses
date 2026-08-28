// mountprobe.cpp — вимірює справжній контракт конкретного монтування (C++20/C++23)
#include <array>
#include <cerrno>
#include <chrono>
#include <filesystem>
#include <format>
#include <iostream>
#include <memory>
#include <span>
#include <string>
#include <string_view>
#include <thread>
#include <vector>

#include <dirent.h>
#include <fcntl.h>
#include <netdb.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <sys/file.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <unistd.h>

namespace fs = std::filesystem;

static int ctl = -1;
static fs::path share_dir;

static double mono() {
    auto now = std::chrono::steady_clock::now();
    auto duration = now.time_since_epoch();
    return std::chrono::duration<double>(duration).count();
}

static void nap_ms(long ms) {
    std::this_thread::sleep_for(std::chrono::milliseconds(ms));
}

static fs::path at(std::string_view name) {
    return share_dir / name;
}

static std::string secs(double v) {
    if (v < 0) return "  > 180";
    return std::format("{:7.2f}", v);
}
