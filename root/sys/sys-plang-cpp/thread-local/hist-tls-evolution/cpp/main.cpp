#include <pthread.h>
#include <memory>
#include <string>
#include <mutex>

namespace legacy_tls {
    static pthread_key_t thread_log_key;
    static std::once_flag key_init_flag;

    static void destroy_cpp_buffer(void* ptr) {
        delete static_cast<std::string*>(ptr);
    }

    void append_log(const std::string& msg) {
        std::call_once(key_init_flag, []() {
            pthread_key_create(&thread_log_key, destroy_cpp_buffer);
        });

        auto* buf = static_cast<std::string*>(pthread_getspecific(thread_log_key));
        if (!buf) {
            buf = new std::string();
            pthread_setspecific(thread_log_key, buf);
        }
        *buf = "Log: " + msg + "\n";
    }
}
