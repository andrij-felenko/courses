#include <jni.h>
#include <android/log.h>
#include <string>
#include <string_view>
#include <memory>
#include <stdexcept>

namespace {
constexpr std::string_view kLogTag = "NativeEngine";

template <typename... Args>
void log_info(std::string_view fmt_str, Args&&... args) {
    std::string msg = (sizeof...(args) == 0) 
        ? std::string(fmt_str) 
        : std::string(fmt_str);
    __android_log_print(ANDROID_LOG_INFO, kLogTag.data(), "%s", msg.c_str());
}

template <typename... Args>
void log_error(std::string_view fmt_str, Args&&... args) {
    __android_log_print(ANDROID_LOG_ERROR, kLogTag.data(), "%s", fmt_str.data());
}

// RAII-обгортка для гарантованого звільнення JNI UTF рядків
class ScopedUtfChars {
public:
    ScopedUtfChars(JNIEnv* env, jstring jstr)
        : env_(env), jstr_(jstr), chars_(env->GetStringUTFChars(jstr, nullptr)) {}

    ~ScopedUtfChars() {
        if (chars_ != nullptr) {
            env_->ReleaseStringUTFChars(jstr_, chars_);
        }
    }

    ScopedUtfChars(const ScopedUtfChars&) = delete;
    ScopedUtfChars& operator=(const ScopedUtfChars&) = delete;

    [[nodiscard]] const char* get() const noexcept { return chars_; }
    [[nodiscard]] std::string_view view() const noexcept {
        return chars_ ? std::string_view(chars_) : std::string_view{};
    }

private:
    JNIEnv* env_;
    jstring jstr_;
    const char* chars_;
};
} // namespace

extern "C" JNIEXPORT jstring JNICALL
Java_com_example_app_NativeBridge_processPayload(
    JNIEnv* env,
    jobject /* thiz */,
    jstring input_str) noexcept
{
    if (input_str == nullptr) {
        log_error("Отримано нульовий покажчик на рядок з Java");
        return nullptr;
    }

    ScopedUtfChars utf_input(env, input_str);
    if (utf_input.get() == nullptr) {
        log_error("Помилка отримання символів UTF-8");
        return nullptr;
    }

    try {
        std::string_view payload = utf_input.view();
        log_info("Обробка корисного навантаження у безпечному контексті C++");

        std::string processed = "Android NDK Output: ";
        processed.append(payload);

        return env->NewStringUTF(processed.c_str());
    } catch (const std::exception& ex) {
        log_error(ex.what());
        return nullptr;
    }
}
