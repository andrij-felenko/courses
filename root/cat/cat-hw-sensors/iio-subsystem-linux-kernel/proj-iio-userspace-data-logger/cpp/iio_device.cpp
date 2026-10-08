#include "iio_device.hpp"
#include <stdexcept>
#include <iostream>

// --- Реалізація IioContext ---

IioContext::IioContext(const std::string& uri) {
    if (uri.empty()) {
        ctx_ = iio_create_default_context();
        if (!ctx_) {
            ctx_ = iio_create_local_context();
        }
    } else {
        ctx_ = iio_create_context_from_uri(uri.c_str());
    }

    if (!ctx_) {
        throw std::runtime_error("Не вдалося створити контекст IIO (перевірте підключення давача або права доступу).");
    }
}

IioContext::~IioContext() {
    if (ctx_) {
        iio_context_destroy(ctx_);
        ctx_ = nullptr;
    }
}

IioContext::IioContext(IioContext&& other) noexcept : ctx_(other.ctx_) {
    other.ctx_ = nullptr;
}

IioContext& IioContext::operator=(IioContext&& other) noexcept {
    if (this != &other) {
        if (ctx_) {
            iio_context_destroy(ctx_);
        }
        ctx_ = other.ctx_;
        other.ctx_ = nullptr;
    }
    return *this;
}

struct iio_device* IioContext::find_device(const std::string& name_or_id) const {
    struct iio_device* dev = iio_context_find_device(ctx_, name_or_id.c_str());
    if (!dev) {
        throw std::runtime_error("Пристрій IIO з ім'ям або ID '" + name_or_id + "' не знайдено.");
    }
    return dev;
}

// --- Реалізація IioBuffer ---

IioBuffer::IioBuffer(struct iio_device* dev, std::size_t samples_count, bool cyclic) {
    if (!dev) {
        throw std::invalid_argument("Передано нульовий вказівник на пристрій IIO.");
    }
    buf_ = iio_device_create_buffer(dev, samples_count, cyclic);
    if (!buf_) {
        throw std::runtime_error("Не вдалося створити кільцевий буфер IIO.");
    }
}

IioBuffer::~IioBuffer() {
    if (buf_) {
        iio_buffer_destroy(buf_);
        buf_ = nullptr;
    }
}

IioBuffer::IioBuffer(IioBuffer&& other) noexcept : buf_(other.buf_) {
    other.buf_ = nullptr;
}

IioBuffer& IioBuffer::operator=(IioBuffer&& other) noexcept {
    if (this != &other) {
        if (buf_) {
            iio_buffer_destroy(buf_);
        }
        buf_ = other.buf_;
        other.buf_ = nullptr;
    }
    return *this;
}

std::ptrdiff_t IioBuffer::refill() {
    std::ptrdiff_t ret = iio_buffer_refill(buf_);
    if (ret < 0) {
        throw std::runtime_error("Помилка під час наповнення буфера IIO (iio_buffer_refill): " + std::to_string(ret));
    }
    return ret;
}

// --- Реалізація IioInertialSensor ---

IioInertialSensor::IioInertialSensor(const std::string& device_name, const std::string& context_uri)
    : context_(context_uri) {
    dev_ = context_.find_device(device_name);
}

struct iio_channel* IioInertialSensor::enable_channel_if_exists(const std::string& ch_name) {
    struct iio_channel* chn = iio_device_find_channel(dev_, ch_name.c_str(), false);
    if (!chn) {
        // Пошук серед усіх каналів за назвою або ідентифікатором
        unsigned int count = iio_device_get_channels_count(dev_);
        for (unsigned int i = 0; i < count; ++i) {
            struct iio_channel* candidate = iio_device_get_channel(dev_, i);
            const char* id = iio_channel_get_id(candidate);
            const char* name = iio_channel_get_name(candidate);
            if ((id && ch_name == id) || (name && ch_name == name)) {
                chn = candidate;
                break;
            }
        }
    }

    if (chn) {
        iio_channel_enable(chn);
    }
    return chn;
}

void IioInertialSensor::configure_channels() {
    // Вмикаємо канали акселерометра
    ch_accel_x_ = enable_channel_if_exists("accel_x");
    if (!ch_accel_x_) ch_accel_x_ = enable_channel_if_exists("in_accel_x_raw");

    ch_accel_y_ = enable_channel_if_exists("accel_y");
    if (!ch_accel_y_) ch_accel_y_ = enable_channel_if_exists("in_accel_y_raw");

    ch_accel_z_ = enable_channel_if_exists("accel_z");
    if (!ch_accel_z_) ch_accel_z_ = enable_channel_if_exists("in_accel_z_raw");

    // Вмикаємо канали гіроскопа
    ch_gyro_x_ = enable_channel_if_exists("angvel_x");
    if (!ch_gyro_x_) ch_gyro_x_ = enable_channel_if_exists("in_angvel_x_raw");

    ch_gyro_y_ = enable_channel_if_exists("angvel_y");
    if (!ch_gyro_y_) ch_gyro_y_ = enable_channel_if_exists("in_angvel_y_raw");

    ch_gyro_z_ = enable_channel_if_exists("angvel_z");
    if (!ch_gyro_z_) ch_gyro_z_ = enable_channel_if_exists("in_angvel_z_raw");

    // Вмикаємо канал системного/апаратного часового штампу
    ch_timestamp_ = enable_channel_if_exists("timestamp");
}

void IioInertialSensor::create_buffer(std::size_t samples_count) {
    buffer_ = std::make_unique<IioBuffer>(dev_, samples_count, false);
}

std::vector<InertialSample> IioInertialSensor::read_samples() {
    if (!buffer_) {
        throw std::runtime_error("Буфер не створено. Спочатку викличте create_buffer().");
    }

    buffer_->refill();

    struct iio_buffer* buf = buffer_->get();
    std::ptrdiff_t step = iio_buffer_step(buf);
    char* end = static_cast<char*>(iio_buffer_end(buf));

    struct iio_channel* ref_ch = ch_accel_x_ ? ch_accel_x_ : ch_timestamp_;
    if (!ref_ch) {
        return {};
    }

    char* first_ptr = static_cast<char*>(iio_buffer_first(buf, ref_ch));
    std::size_t num_samples = 0;
    if (first_ptr < end && step > 0) {
        num_samples = static_cast<std::size_t>((end - first_ptr) / step);
    }

    std::vector<InertialSample> samples;
    samples.reserve(num_samples);

    for (char* ptr = first_ptr; ptr < end; ptr += step) {
        InertialSample sample{};

        if (ch_accel_x_) iio_channel_convert(ch_accel_x_, &sample.accel_x, ptr);
        if (ch_accel_y_) iio_channel_convert(ch_accel_y_, &sample.accel_y, ptr);
        if (ch_accel_z_) iio_channel_convert(ch_accel_z_, &sample.accel_z, ptr);

        if (ch_gyro_x_) iio_channel_convert(ch_gyro_x_, &sample.gyro_x, ptr);
        if (ch_gyro_y_) iio_channel_convert(ch_gyro_y_, &sample.gyro_y, ptr);
        if (ch_gyro_z_) iio_channel_convert(ch_gyro_z_, &sample.gyro_z, ptr);

        if (ch_timestamp_) {
            int64_t ts_ns = 0;
            iio_channel_convert(ch_timestamp_, &ts_ns, ptr);
            sample.timestamp_sec = static_cast<double>(ts_ns) / 1e9;
        } else {
            auto now = std::chrono::steady_clock::now().time_since_epoch();
            sample.timestamp_sec = std::chrono::duration<double>(now).count();
        }

        samples.push_back(sample);
    }

    return samples;
}

// --- Реалізація FrameRateCalculator ---

FrameRateCalculator::FrameRateCalculator(std::size_t window_size)
    : window_size_(window_size), last_time_(std::chrono::steady_clock::now()) {}

void FrameRateCalculator::update(std::size_t sample_count) {
    accumulated_samples_ += sample_count;
    ready_ = false;

    if (accumulated_samples_ >= window_size_) {
        auto now = std::chrono::steady_clock::now();
        std::chrono::duration<double> elapsed = now - last_time_;
        if (elapsed.count() > 0.0) {
            current_fps_ = static_cast<double>(accumulated_samples_) / elapsed.count();
            ready_ = true;
        }
        accumulated_samples_ = 0;
        last_time_ = now;
    }
}
