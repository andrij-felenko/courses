#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <chrono>
#include <thread>
#include <utility>
#include <iomanip>
#include <algorithm>
#include <cstdint>
#include <cerrno>
#include <ctime>
#include <unistd.h>
#include <sys/resource.h>
#include <sys/syscall.h>

// Прочитати невеликий файл цілком у std::string.
static std::string slurp(std::string_view path)
{
    std::ifstream f{std::string(path)};   // string_view не зобов'язаний бути з нулем на кінці
    if (!f.is_open()) return {};
    std::ostringstream ss;
    ss << f.rdbuf();
    return ss.str();
}

// Настінний монотонний час через std::chrono::steady_clock.
static auto now_mono()
{
    return std::chrono::steady_clock::now();
}

static double clk_tck()
{
    static double hz = static_cast<double>(sysconf(_SC_CLK_TCK));
    return hz;
}
