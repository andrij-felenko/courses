#include <mutex>
#include <memory>

class HardwareRegistry {
public:
    static HardwareRegistry& instance() {
        std::call_once(s_init_flag, []() {
            s_instance.reset(new HardwareRegistry());
        });
        return *s_instance;
    }

private:
    HardwareRegistry() = default;
    static inline std::unique_ptr<HardwareRegistry> s_instance;
    static inline std::once_flag s_init_flag;
};
