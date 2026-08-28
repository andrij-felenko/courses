namespace physics::mechanics {

using LogCallback = void(*)(std::string_view message, int level);

class Logger {
public:
    static void setCallback(LogCallback cb) noexcept {}
};

}
