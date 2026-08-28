#include <iostream>
#include <memory>
#include <vector>
#include <string>
#include <chrono>
#include <thread>
#include <map>
#include <sys/mman.h>
#include <unistd.h>

#include <libcamera/libcamera.h>
#include <libcamera/control_ids.h>
#include <libcamera/property_ids.h>

using namespace libcamera;

// Структура для збереження адреси відображення площини пам'яті DMA-BUF у віртуальний простір
struct MappedPlane {
    void *memory{nullptr};
    size_t length{0};
};

struct MappedBuffer {
    std::vector<MappedPlane> planes;
};

// Головний клас керування конвеєром камери
class CameraCaptureApp {
public:
    CameraCaptureApp() : cameraManager_(std::make_unique<CameraManager>()) {}

    ~CameraCaptureApp() {
        stop();
    }

    bool initialize() {
        int ret = cameraManager_->start();
        if (ret) {
            std::cerr << "Помилка запуску CameraManager: " << ret << std::endl;
            return false;
        }

        auto cameras = cameraManager_->cameras();
        if (cameras.empty()) {
            std::cerr << "У системі не знайдено жодної доступної камери!" << std::endl;
            return false;
        }

        // Обираємо першу доступну камеру в системі
        camera_ = cameras[0];
        std::cout << "Знайдено камеру: " << camera_->id() << std::endl;

        // Блокуємо камеру для ексклюзивного використання поточним процесом
        if (camera_->acquire()) {
            std::cerr << "Не вдалося отримати монопольний доступ до камери." << std::endl;
            return false;
        }

        return configureStreams();
    }

    bool startCapture(unsigned int frameCount = 30) {
        if (!allocateBuffers()) {
            return false;
        }

        // Підключаємо слот зворотного виклику до сигналу завершення запиту
        camera_->requestCompleted.connect(this, &CameraCaptureApp::onRequestCompleted);

        // Запуск апаратного конвеєра передачі кадрів
        if (camera_->start()) {
            std::cerr << "Помилка виклику Camera::start()" << std::endl;
            return false;
        }

        std::cout << "Апаратний конвеєр успішно запущено. Передача запитів у ядро..." << std::endl;

        // Чергуємо всі сформовані запити в чергу обробки
        for (auto &request : requests_) {
            if (camera_->queueRequest(request.get()) < 0) {
                std::cerr << "Не вдалося поставити запит у чергу камери!" << std::endl;
                return false;
            }
        }

        // Запускаємо цикл обробки подій до досягнення заданої кількості кадрів
        targetFrames_ = frameCount;
        while (completedFrames_ < targetFrames_) {
            cameraManager_->eventDispatcher()->processEvents();
        }

        return true;
    }

    void stop() {
        if (camera_) {
            camera_->stop();
            camera_->requestCompleted.disconnect(this, &CameraCaptureApp::onRequestCompleted);
            
            // Звільняємо відображену пам'ять dma-buf
            for (auto &[buffer, mapped] : mappedBuffers_) {
                for (auto &plane : mapped.planes) {
                    if (plane.memory) {
                        munmap(plane.memory, plane.length);
                    }
                }
            }
            mappedBuffers_.clear();
            requests_.clear();
            allocator_.reset();

            camera_->release();
            camera_.reset();
        }

        if (cameraManager_) {
            cameraManager_->stop();
        }
    }

private:
    bool configureStreams() {
        // Запитуємо бажані ролі потоків: Viewfinder (відображення) та StillCapture (знімок)
        std::vector<StreamRole> roles = { StreamRole::Viewfinder, StreamRole::StillCapture };
        config_ = camera_->generateConfiguration(roles);
        if (!config_) {
            std::cerr << "Помилка генерації конфігурації для обраних ролей." << std::endl;
            return false;
        }

        // Налаштовуємо параметри першого потоку (Viewfinder — швидкий NV12 1280x720)
        StreamConfiguration &vfConfig = config_->at(0);
        vfConfig.pixelFormat = formats::NV12;
        vfConfig.size.width = 1280;
        vfConfig.size.height = 720;

        // Налаштовуємо параметри другого потоку (StillCapture — повний RGB888 1920x1080)
        StreamConfiguration &stillConfig = config_->at(1);
        stillConfig.pixelFormat = formats::BGR888;
        stillConfig.size.width = 1920;
        stillConfig.size.height = 1080;

        // Валідація конфігурації: узгодження обмежень ISP та сенсора
        CameraConfiguration::Status status = config_->validate();
        if (status == CameraConfiguration::Invalid) {
            std::cerr << "Конфігурація камери не підтримується апаратурою!" << std::endl;
            return false;
        } else if (status == CameraConfiguration::Adjusted) {
            std::cout << "Конфігурацію було автоматично скориговано драйвером під можливості ISP." << std::endl;
        }

        // Застосовуємо конфігурацію до апаратного драйвера
        if (camera_->configure(config_.get()) < 0) {
            std::cerr << "Помилка застосування конфігурації Camera::configure()" << std::endl;
            return false;
        }

        std::cout << "Конфігурація успішно застосована:" << std::endl;
        std::cout << "  Потік 0 (Viewfinder): " << vfConfig.toString() << std::endl;
        std::cout << "  Потік 1 (StillCapture): " << stillConfig.toString() << std::endl;

        return true;
    }

    bool allocateBuffers() {
        allocator_ = std::make_unique<FrameBufferAllocator>(camera_);

        for (StreamConfiguration &cfg : *config_) {
            Stream *stream = cfg.stream();
            if (allocator_->allocate(stream) < 0) {
                std::cerr << "Помилка виділення буферів для потоку " << stream << std::endl;
                return false;
            }

            const auto &buffers = allocator_->buffers(stream);
            std::cout << "Виділено " << buffers.size() << " буферів для потоку " << stream << std::endl;

            // Відображаємо dma-buf дескриптори в пам'ять процесу для читання пікселів
            for (const auto &buffer : buffers) {
                MappedBuffer mapped;
                for (const FrameBuffer::Plane &plane : buffer->planes()) {
                    void *mem = mmap(nullptr, plane.length, PROT_READ | PROT_WRITE,
                                     MAP_SHARED, plane.fd.get(), plane.offset);
                    if (mem == MAP_FAILED) {
                        std::cerr << "Помилка mmap dma-buf fd: " << plane.fd.get() << std::endl;
                        return false;
                    }
                    mapped.planes.push_back({ mem, plane.length });
                }
                mappedBuffers_[buffer.get()] = mapped;
            }
        }

        // Створюємо множину запитів (Requests), прив'язуючи відповідні буфери
        Stream *vfStream = config_->at(0).stream();
        Stream *stillStream = config_->at(1).stream();
        const auto &vfBuffers = allocator_->buffers(vfStream);
        const auto &stillBuffers = allocator_->buffers(stillStream);

        size_t numRequests = std::min(vfBuffers.size(), stillBuffers.size());
        for (size_t i = 0; i < numRequests; ++i) {
            std::unique_ptr<Request> request = camera_->createRequest();
            if (!request) {
                std::cerr << "Не вдалося створити об'єкт Request." << std::endl;
                return false;
            }

            // Додаємо буфери кожного потоку до одного запиту
            request->addBuffer(vfStream, vfBuffers[i].get());
            request->addBuffer(stillStream, stillBuffers[i].get());

            // Встановлюємо початкові динамічні елементи керування для кадру
            ControlList &controls = request->controls();
            controls.set(controls::ExposureTime, 15000);   // 15 мс (15000 мікросекунд)
            controls.set(controls::AnalogueGain, 1.5f);     // Підсилення сенсора 1.5x
            controls.set(controls::AfMode, controls::AfModeContinuous); // Автофокус

            requests_.push_back(std::move(request));
        }

        return true;
    }

    void onRequestCompleted(Request *request) {
        if (request->status() == Request::RequestCancelled) {
            std::cout << "Запит було скасовано." << std::endl;
            return;
        }

        completedFrames_++;

        // Отримання метаданих, розрахованих ядром та модулем IPA для цього конкретного кадру
        const ControlList &metadata = request->metadata();
        auto expTime = metadata.get(controls::ExposureTime);
        auto sensorGain = metadata.get(controls::AnalogueGain);

        std::cout << "[Кадр #" << completedFrames_ << "] Захоплено! ";
        if (expTime) std::cout << "Витримка: " << *expTime << " мкс, ";
        if (sensorGain) std::cout << "Підсилення: " << *sensorGain << "x";
        std::cout << std::endl;

        // Доступ до даних потоку Viewfinder
        Stream *vfStream = config_->at(0).stream();
        FrameBuffer *buffer = request->findBuffer(vfStream);
        if (buffer) {
            const FrameMetadata &fmd = buffer->metadata();
            const MappedBuffer &mapped = mappedBuffers_[buffer];
            
            auto *yPlane = static_cast<const uint8_t*>(mapped.planes[0].memory);
            std::cout << "  Viewfinder: розмір=" << fmd.planes()[0].bytesused
                      << " байт, таймстемп=" << fmd.timestamp / 1000000 << " мс"
                      << ", центр пікселя Y=" << static_cast<int>(yPlane[1280 * 360 + 640])
                      << std::endl;
        }

        // Перевикористання запиту для наступного кадру в нескінченному конвеєрі
        if (completedFrames_ + requests_.size() <= targetFrames_) {
            request->reuse(Request::ReuseBuffers);
            
            // Динамічно змінюємо експозицію кожного наступного запиту
            request->controls().set(controls::ExposureTime, 10000 + (completedFrames_ % 10) * 2000);
            camera_->queueRequest(request);
        }
    }

    std::unique_ptr<CameraManager> cameraManager_;
    std::shared_ptr<Camera> camera_;
    std::unique_ptr<CameraConfiguration> config_;
    std::unique_ptr<FrameBufferAllocator> allocator_;
    std::vector<std::unique_ptr<Request>> requests_;
    std::map<FrameBuffer*, MappedBuffer> mappedBuffers_;

    unsigned int targetFrames_{0};
    unsigned int completedFrames_{0};
};

int main() {
    CameraCaptureApp app;
    if (!app.initialize()) {
        return 1;
    }

    std::cout << "Початок захоплення серії з 20 кадрів..." << std::endl;
    if (!app.startCapture(20)) {
        return 1;
    }

    std::cout << "Серію успішно завершено. Ресурси звільнено." << std::endl;
    return 0;
}
