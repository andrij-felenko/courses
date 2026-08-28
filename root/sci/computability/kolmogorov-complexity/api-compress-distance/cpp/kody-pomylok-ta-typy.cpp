// ncd.hpp — Перелічувачі та конфігурація в C++
namespace ncd {

enum class Error : int {
    Success           =  0,
    NullPointer       = -1,
    EmptyBuffer       = -2,
    AllocFailed       = -3,
    CompressFail      = -4,
    InvalidEngine     = -5
};

enum class Engine {
    Zlib,
    Bzip2,
    Lzma,
    Zstd
};

struct Config {
    Engine engine = Engine::Zstd;
    int compression_level = 3;
    size_t window_size = 0; // 0 = default for engine
    unsigned int threads = std::thread::hardware_concurrency();
};

} // namespace ncd
