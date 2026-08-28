// C++ (C++20): Обгортка RAII навколо LittleCMS C-API для автоматичного керування ресурсами
#include <lcms2.h>
#include <memory>
#include <span>
#include <stdexcept>

namespace lcms {

struct ProfileDeleter {
    void operator()(cmsHPROFILE handle) const noexcept {
        if (handle) {
            cmsCloseProfile(handle);
        }
    }
};

struct TransformDeleter {
    void operator()(cmsHTRANSFORM handle) const noexcept {
        if (handle) {
            cmsDeleteTransform(handle);
        }
    }
};

using UniqueProfile = std::unique_ptr<void, ProfileDeleter>;
using UniqueTransform = std::unique_ptr<void, TransformDeleter>;

class ColorTransform {
private:
    UniqueTransform transform_;

public:
    ColorTransform(const UniqueProfile& in_profile, cmsUInt32Number in_format,
                   const UniqueProfile& out_profile, cmsUInt32Number out_format,
                   cmsUInt32Number intent = INTENT_PERCEPTUAL, cmsUInt32Number flags = 0) {
        cmsHTRANSFORM handle = cmsCreateTransform(
            in_profile.get(), in_format,
            out_profile.get(), out_format,
            intent, flags
        );
        if (!handle) {
            throw std::runtime_error("Не вдалося створити колірну трансформацію CMM");
        }
        transform_.reset(handle);
    }

    template <typename T_In, typename T_Out>
    void transform(std::span<const T_In> in_buffer, std::span<T_Out> out_buffer) const {
        if (in_buffer.size() > out_buffer.size()) {
            throw std::invalid_argument("Розмір вихідного буфера менший за вхідний");
        }
        cmsDoTransform(transform_.get(), in_buffer.data(), out_buffer.data(),
                       static_cast<cmsUInt32Number>(in_buffer.size()));
    }
};

} // namespace lcms
