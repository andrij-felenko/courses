#include <iostream>
#include <string_view>
#include <span>
#include <array>
#include <expected>
#include <cstring>
#include <stdexcept>
#include <openthread/instance.h>
#include <openthread/ip6.h>
#include <openthread/thread.h>
#include <openthread/dataset.h>
#include <openthread/udp.h>
#include <openthread/coap.h>
#include <openthread/joiner.h>
#include <openthread/tasklet.h>

namespace thread_mesh {

enum class DeviceRole {
    Disabled,
    Detached,
    Child,
    Router,
    Leader,
    Unknown
};

class ThreadNode {
public:
    ThreadNode() {
        instance_ = otInstanceInitSingle();
        if (!instance_) {
            throw std::runtime_error("Не вдалося ініціалізувати екземпляр OpenThread");
        }
        otSetStateChangedCallback(instance_, &ThreadNode::onStateChangedStatic, this);
    }

    ~ThreadNode() {
        if (coapStarted_) {
            otCoapStop(instance_);
        }
        if (socketOpened_) {
            otUdpClose(instance_, &socket_);
        }
        if (instance_) {
            otInstanceFinalize(instance_);
        }
    }

    ThreadNode(const ThreadNode&) = delete;
    ThreadNode& operator=(const ThreadNode&) = delete;
    ThreadNode(ThreadNode&&) noexcept = delete;
    ThreadNode& operator=(ThreadNode&&) noexcept = delete;

    void configureNetwork(uint16_t channel, uint16_t panId, 
                          std::span<const uint8_t, 16> networkKey, 
                          std::string_view networkName) 
    {
        otOperationalDataset dataset{};
        dataset.mChannel = channel;
        dataset.mComponents.mIsChannelPresent = true;

        dataset.mPanId = static_cast<otPanId>(panId);
        dataset.mComponents.mIsPanIdPresent = true;

        std::memcpy(dataset.mNetworkKey.m8, networkKey.data(), networkKey.size());
        dataset.mComponents.mIsNetworkKeyPresent = true;

        size_t nameLen = std::min(networkName.size(), sizeof(dataset.mNetworkName.m8) - 1);
        std::memcpy(dataset.mNetworkName.m8, networkName.data(), nameLen);
        dataset.mNetworkName.m8[nameLen] = '\0';
        dataset.mComponents.mIsNetworkNamePresent = true;

        otDatasetSetActive(instance_, &dataset);
    }

    void start() {
        otIp6SetEnabled(instance_, true);
        otThreadSetEnabled(instance_, true);
    }

    void openUdpPort(uint16_t port) {
        std::memset(&socket_, 0, sizeof(socket_));
        otUdpOpen(instance_, &socket_, &ThreadNode::onUdpReceiveStatic, this);
        
        otSockAddr sockAddr{};
        sockAddr.mPort = port;
        otUdpBind(instance_, &socket_, &sockAddr, OT_NETIF_THREAD);
        socketOpened_ = true;
    }

    void enableCoapService() {
        otCoapStart(instance_, OT_DEFAULT_COAP_PORT);
        std::memset(&tempResource_, 0, sizeof(tempResource_));
        tempResource_.mUriPath = "sensors/temp";
        tempResource_.mHandler = &ThreadNode::onCoapTempRequestStatic;
        tempResource_.mContext = this;
        otCoapAddResource(instance_, &tempResource_);
        coapStarted_ = true;
    }

    std::expected<void, otError> sendUdp(std::string_view destIp, uint16_t port, std::string_view payload) {
        otMessageInfo messageInfo{};
        otIp6AddressFromString(destIp.data(), &messageInfo.mPeerAddr);
        messageInfo.mPeerPort = port;

        otMessage *msg = otUdpNewMessage(instance_, nullptr);
        if (!msg) {
            return std::unexpected(OT_ERROR_NO_BUFS);
        }

        otError err = otMessageAppend(msg, payload.data(), static_cast<uint16_t>(payload.size()));
        if (err != OT_ERROR_NONE) {
            otMessageFree(msg);
            return std::unexpected(err);
        }

        err = otUdpSend(instance_, &socket_, msg, &messageInfo);
        if (err != OT_ERROR_NONE) {
            otMessageFree(msg);
            return std::unexpected(err);
        }

        return {};
    }

    void processTasks() {
        otTaskletsProcess(instance_);
    }

    bool hasPendingTasks() const noexcept {
        return otTaskletsArePending(instance_);
    }

private:
    static void onStateChangedStatic(otChangedFlags flags, void *context) {
        static_cast<ThreadNode*>(context)->onStateChanged(flags);
    }

    static void onUdpReceiveStatic(void *context, otMessage *msg, const otMessageInfo *info) {
        static_cast<ThreadNode*>(context)->onUdpReceive(msg, info);
    }

    static void onCoapTempRequestStatic(void *context, otMessage *msg, const otMessageInfo *info) {
        static_cast<ThreadNode*>(context)->onCoapTempRequest(msg, info);
    }

    void onStateChanged(otChangedFlags flags) {
        if (flags & OT_CHANGED_THREAD_ROLE) {
            otDeviceRole r = otThreadGetDeviceRole(instance_);
            DeviceRole role = DeviceRole::Unknown;
            switch (r) {
            case OT_DEVICE_ROLE_DISABLED: role = DeviceRole::Disabled; break;
            case OT_DEVICE_ROLE_DETACHED: role_str = DeviceRole::Detached; break;
            case OT_DEVICE_ROLE_CHILD:    role = DeviceRole::Child; break;
            case OT_DEVICE_ROLE_ROUTER:   role = DeviceRole::Router; break;
            case OT_DEVICE_ROLE_LEADER:   role = DeviceRole::Leader; break;
            }
            std::cout << "[C++ Thread] Зміна ролі -> " << static_cast<int>(role) << std::endl;
        }
    }

    void onUdpReceive(otMessage *message, const otMessageInfo *messageInfo) {
        char buf[128];
        uint16_t len = otMessageGetLength(message) - otMessageGetOffset(message);
        len = std::min<uint16_t>(len, sizeof(buf) - 1);

        otMessageRead(message, otMessageGetOffset(message), buf, len);
        buf[len] = '\0';

        char ipStr[OT_IP6_ADDRESS_STRING_SIZE];
        otIp6AddressToString(&messageInfo->mPeerAddr, ipStr, sizeof(ipStr));

        std::cout << "[C++ UDP Rx] Від [" << ipStr << "]:" << messageInfo->mPeerPort << " -> " << buf << std::endl;
    }

    void onCoapTempRequest(otMessage *message, const otMessageInfo *messageInfo) {
        if (otCoapMessageGetCode(message) == OT_COAP_CODE_GET) {
            otMessage *response = otCoapNewMessage(instance_, nullptr);
            if (!response) return;

            otCoapMessageInitResponse(response, message, OT_COAP_TYPE_ACKNOWLEDGMENT, OT_COAP_CODE_CONTENT);
            otCoapMessageSetFormat(response, OT_COAP_OPTION_CONTENT_FORMAT_TEXT_PLAIN);

            constexpr std::string_view payload = "{\"temp\": 23.5, \"unit\": \"C\"}";
            otCoapMessageSetPayloadMarker(response);
            otMessageAppend(response, payload.data(), static_cast<uint16_t>(payload.size()));

            otCoapSendResponse(instance_, response, messageInfo);
            std::cout << "[C++ CoAP] Відправлено відповідь на GET /sensors/temp" << std::endl;
        }
    }

    otInstance *instance_{nullptr};
    otUdpSocket socket_{};
    otCoapResource tempResource_{};
    bool socketOpened_{false};
    bool coapStarted_{false};
};

} // namespace thread_mesh

int main() {
    using namespace thread_mesh;
    try {
        ThreadNode node;
        constexpr std::array<uint8_t, 16> netKey = {
            0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
            0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff
        };

        node.configureNetwork(15, 0x1234, netKey, "Thread-OpenLab");
        node.start();
        node.openUdpPort(12345);
        node.enableCoapService();

        std::cout << "Вузол Thread ініціалізовано. Очікування входження в мережу..." << std::endl;

        while (true) {
            node.processTasks();
            if (!node.hasPendingTasks()) {
                /* Очікування наступної системної події */
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "Фатальна помилка: " << e.what() << std::endl;
        return -1;
    }
    return 0;
}
