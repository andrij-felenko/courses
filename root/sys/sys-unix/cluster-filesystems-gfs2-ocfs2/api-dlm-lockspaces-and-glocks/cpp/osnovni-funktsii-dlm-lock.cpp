#include <libdlm.h>
#include <string_view>
#include <functional>
#include <stdexcept>
#include <system_error>

/* C++ клас керування простором блокувань та RAII-блокуваннями */
class DlmLockspace {
public:
    explicit DlmLockspace(std::string_view name) {
        handle_ = dlm_open_lockspace(name.data());
        if (!handle_) {
            handle_ = dlm_create_lockspace(name.data(), 0660);
        }
        if (!handle_) {
            throw std::system_error(errno, std::generic_category(), "Failed to open or create DLM lockspace");
        }
    }

    ~DlmLockspace() {
        if (handle_) {
            dlm_release_lockspace(handle_);
        }
    }

    DlmLockspace(const DlmLockspace&) = delete;
    DlmLockspace& operator=(const DlmLockspace&) = delete;

    [[nodiscard]] dlm_lshandle_t native_handle() const noexcept { return handle_; }

private:
    dlm_lshandle_t handle_{nullptr};
};
