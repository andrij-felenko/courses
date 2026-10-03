#include "MjpegStreamer.hpp"
#include "esp_log.h"
#include "lwip/sockets.h"
#include "lwip/netdb.h"
#include <cstdio>
#include <cstring>

static const char* TAG = "MjpegStreamer";

namespace camera {

MjpegStreamer::MjpegStreamer(uint16_t port)
    : port_(port) {}

MjpegStreamer::~MjpegStreamer() {
    stop();
}

esp_err_t MjpegStreamer::start(FrameServer& server, UBaseType_t priority, uint32_t stackSize) {
    if (running_) {
        return ESP_OK;
    }

    server_ = &server;

    // Реєструємося як підписник кадрового сервера
    frameQueue_ = server_->registerSubscriber(3);
    if (!frameQueue_) {
        ESP_LOGE(TAG, "Не вдалося зареєструвати підписника в FrameServer");
        return ESP_FAIL;
    }

    running_ = true;

    BaseType_t ret = xTaskCreatePinnedToCore(
        streamerTask,
        "MjpegStreamTask",
        stackSize,
        this,
        priority,
        &taskHandle_,
        0 // Запускаємо мережеву задачу на ядрі 0
    );

    if (ret != pdPASS) {
        running_ = false;
        server_->unregisterSubscriber(frameQueue_);
        frameQueue_ = nullptr;
        ESP_LOGE(TAG, "Помилка створення задачі MjpegStreamer");
        return ESP_FAIL;
    }

    ESP_LOGI(TAG, "MJPEG передавач запущено на порту %u", port_);
    return ESP_OK;
}

esp_err_t MjpegStreamer::stop() {
    if (!running_) {
        return ESP_OK;
    }

    running_ = false;
    if (server_ && frameQueue_) {
        server_->unregisterSubscriber(frameQueue_);
        frameQueue_ = nullptr;
    }

    if (taskHandle_) {
        vTaskDelay(pdMS_TO_TICKS(100));
        taskHandle_ = nullptr;
    }

    ESP_LOGI(TAG, "MJPEG передавач зупинено");
    return ESP_OK;
}

void MjpegStreamer::streamerTask(void* arg) {
    auto* self = static_cast<MjpegStreamer*>(arg);
    self->runServer();
    vTaskDelete(nullptr);
}

void MjpegStreamer::runServer() {
    int listenFd = socket(AF_INET, SOCK_STREAM, IPPROTO_IP);
    if (listenFd < 0) {
        ESP_LOGE(TAG, "Помилка створення сокета: errno %d", errno);
        return;
    }

    int opt = 1;
    setsockopt(listenFd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in serverAddr = {};
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = htonl(INADDR_ANY);
    serverAddr.sin_port = htons(port_);

    if (bind(listenFd, reinterpret_cast<sockaddr*>(&serverAddr), sizeof(serverAddr)) < 0) {
        ESP_LOGE(TAG, "Помилка прив'язки сокета (bind): errno %d", errno);
        close(listenFd);
        return;
    }

    if (listen(listenFd, 4) < 0) {
        ESP_LOGE(TAG, "Помилка прослуховування сокета (listen): errno %d", errno);
        close(listenFd);
        return;
    }

    ESP_LOGI(TAG, "HTTP MJPEG сервер слухає порт %u...", port_);

    FrameBuffer::Ptr* framePtrContainer = nullptr;

    while (running_) {
        sockaddr_in clientAddr = {};
        socklen_t addrLen = sizeof(clientAddr);
        int clientFd = accept(listenFd, reinterpret_cast<sockaddr*>(&clientAddr), &addrLen);

        if (clientFd < 0) {
            vTaskDelay(pdMS_TO_TICKS(10));
            continue;
        }

        activeClients_++;
        ESP_LOGI(TAG, "Нове підключення клієнта MJPEG потоку");

        // Надсилаємо заголовок HTTP multipart
        const char* httpHeader = 
            "HTTP/1.1 200 OK\r\n"
            "Access-Control-Allow-Origin: *\r\n"
            "Content-Type: multipart/x-mixed-replace; boundary=123456789000000000000987654321\r\n\r\n";
        send(clientFd, httpHeader, strlen(httpHeader), 0);

        // Потокова передача кадрів підключеному клієнту
        while (running_) {
            if (xQueueReceive(frameQueue_, &framePtrContainer, pdMS_TO_TICKS(50)) == pdTRUE) {
                if (framePtrContainer && *framePtrContainer) {
                    FrameBuffer::Ptr frame = *framePtrContainer;
                    delete framePtrContainer;

                    sendMjpegFrame(clientFd, frame);
                }
            }

            // Перевірка активності сокета
            int error = 0;
            socklen_t len = sizeof(error);
            if (getsockopt(clientFd, SOL_SOCKET, SO_ERROR, &error, &len) < 0 || error != 0) {
                break; // Клієнт відключився
            }
        }

        close(clientFd);
        activeClients_--;
        ESP_LOGI(TAG, "Клієнт MJPEG відключився");
    }

    close(listenFd);
}

void MjpegStreamer::sendMjpegFrame(int socketFd, const FrameBuffer::Ptr& frame) {
    if (!frame || frame->actualSize() == 0) return;

    char partHeader[128];
    int headerLen = snprintf(partHeader, sizeof(partHeader),
        "--123456789000000000000987654321\r\n"
        "Content-Type: image/jpeg\r\n"
        "Content-Length: %zu\r\n\r\n",
        frame->actualSize());

    if (send(socketFd, partHeader, headerLen, 0) < 0) return;
    if (send(socketFd, frame->data(), frame->actualSize(), 0) < 0) return;
    send(socketFd, "\r\n", 2, 0);
}

} // namespace camera
