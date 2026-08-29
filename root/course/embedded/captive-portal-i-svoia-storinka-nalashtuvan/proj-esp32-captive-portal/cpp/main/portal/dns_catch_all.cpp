#include "portal/dns_catch_all.hpp"

#include <array>
#include <cerrno>
#include <cstring>
#include <optional>
#include <span>

#include <arpa/inet.h>
#include <netinet/in.h>

#include "esp_log.h"

namespace portal::dns {
namespace {

constexpr const char *kTag = "dns";

/* Зміщення полів заголовка DNS. */
enum Offset : std::size_t {
    kFlags = 2,
    kQdCount = 4,
    kAnCount = 6,
    kNsCount = 8,
    kArCount = 10,
    kHeaderLength = 12,
};

constexpr std::size_t kAnswerLength = 16;  /* вказівник 2 + type 2 + class 2 + TTL 4 + len 2 + IPv4 4 */
constexpr std::uint16_t kTtlSeconds = 10;
constexpr std::uint16_t kTypeA = 1;
constexpr std::uint16_t kClassIn = 1;

[[nodiscard]] std::uint16_t readU16(std::span<const std::uint8_t> packet,
                                    std::size_t offset) noexcept
{
    return static_cast<std::uint16_t>((packet[offset] << 8) | packet[offset + 1]);
}

void writeU16(std::span<std::uint8_t> packet, std::size_t offset,
              std::uint16_t value) noexcept
{
    packet[offset] = static_cast<std::uint8_t>(value >> 8);
    packet[offset + 1] = static_cast<std::uint8_t>(value & 0xFF);
}

/*
 * Знаходить, де закінчується секція питання: послідовність міток
 * «довжина + байти», нульова мітка, далі QTYPE і QCLASS.
 *
 * Дописувати відповідь наосліп у кінець отриманого пакета не можна:
 * Android і сучасні резолвери додають запис OPT (EDNS0) у секцію
 * додаткових, і відповідь, приліплена після нього, виходить зіпсованою.
 * Тому ми обрізаємо пакет саме тут, а лічильник ARCOUNT обнуляємо.
 */
[[nodiscard]] std::optional<std::size_t> questionSectionEnd(
    std::span<const std::uint8_t> query) noexcept
{
    std::size_t offset = kHeaderLength;

    while (offset < query.size()) {
        const std::uint8_t label = query[offset];

        if (label == 0) {
            offset += 1 + 4;  /* нульова мітка + QTYPE + QCLASS */
            if (offset > query.size()) {
                return std::nullopt;
            }
            return offset;
        }

        /* Стиснене посилання в секції питання неприпустиме за RFC 1035. */
        if ((label & 0xC0) != 0) {
            return std::nullopt;
        }

        offset += 1U + label;
    }

    return std::nullopt;
}

/*
 * Перетворює запит на відповідь прямо в буфері й повертає її довжину.
 * Порожній результат означає «відповідати нема на що».
 */
[[nodiscard]] std::optional<std::size_t> buildResponse(std::span<std::uint8_t> packet,
                                                       std::size_t queryLength,
                                                       std::uint32_t answerIp) noexcept
{
    if (queryLength < kHeaderLength) {
        return std::nullopt;
    }

    const std::span<const std::uint8_t> query = packet.first(queryLength);

    const std::uint16_t flags = readU16(query, kFlags);
    if ((flags & 0x8000) != 0) {
        return std::nullopt;  /* це вже відповідь, а не запит */
    }
    if (((flags >> 11) & 0x0F) != 0) {
        return std::nullopt;  /* OPCODE != QUERY: не наша справа */
    }
    if (readU16(query, kQdCount) != 1) {
        return std::nullopt;
    }

    const auto questionEnd = questionSectionEnd(query);
    if (!questionEnd) {
        return std::nullopt;
    }

    const std::uint16_t queryType = readU16(query, *questionEnd - 4);
    const std::uint16_t queryClass = readU16(query, *questionEnd - 2);

    /* QR=1, AA=1, RD переносимо з запиту як є; RA=1, RCODE=0. */
    packet[kFlags] = static_cast<std::uint8_t>(0x84 | (packet[kFlags] & 0x01));
    packet[kFlags + 1] = 0x80;

    writeU16(packet, kNsCount, 0);
    writeU16(packet, kArCount, 0);

    if (queryType != kTypeA || queryClass != kClassIn) {
        /*
         * На AAAA та інші типи віддаємо порожню відповідь без помилки.
         * Клієнт із цього робить висновок «запису такого типу немає»
         * і перепитує адресу типом A — тобто приходить туди, де ми
         * його й чекаємо. Помилка ж (NXDOMAIN) навпаки змусила б
         * телефон вважати мережу непрацездатною.
         */
        writeU16(packet, kAnCount, 0);
        return *questionEnd;
    }

    if (*questionEnd + kAnswerLength > packet.size()) {
        return std::nullopt;
    }

    writeU16(packet, kAnCount, 1);

    const std::span<std::uint8_t> answer =
        packet.subspan(*questionEnd, kAnswerLength);

    /* Ім'я не повторюємо: вказівник 0xC00C посилається на QNAME у питанні. */
    answer[0] = 0xC0;
    answer[1] = static_cast<std::uint8_t>(kHeaderLength);
    writeU16(answer, 2, kTypeA);
    writeU16(answer, 4, kClassIn);
    writeU16(answer, 6, 0);
    writeU16(answer, 8, kTtlSeconds);
    writeU16(answer, 10, 4);
    /* Адреса вже у мережевому порядку байтів — кладемо як є. */
    std::memcpy(answer.data() + 12, &answerIp, sizeof(answerIp));

    return *questionEnd + kAnswerLength;
}

}  // namespace

Status CatchAllServer::start() noexcept
{
    if (running_.load()) {
        return std::unexpected(ESP_ERR_INVALID_STATE);
    }

    UniqueSocket socket{::socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)};
    if (!socket) {
        ESP_LOGE(kTag, "Не вдалося створити UDP-сокет: %d", errno);
        return std::unexpected(ESP_FAIL);
    }

    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = htonl(INADDR_ANY);
    address.sin_port = htons(kPort);

    if (::bind(socket.get(), reinterpret_cast<const sockaddr *>(&address),
               sizeof(address)) < 0) {
        ESP_LOGE(kTag, "Порт 53 зайнято або недоступний: %d", errno);
        return std::unexpected(ESP_FAIL);
    }

    /* Сокет переходить під опіку об'єкта; далі його закриє саме завдання. */
    socket_ = std::move(socket);
    running_.store(true);

    if (xTaskCreate(&CatchAllServer::taskEntry, "dns_server", kTaskStack, this,
                    kTaskPriority, &task_) != pdPASS) {
        running_.store(false);
        socket_.reset();
        return std::unexpected(ESP_ERR_NO_MEM);
    }

    ESP_LOGI(kTag, "Catch-all DNS слухає порт %u", static_cast<unsigned>(kPort));
    return {};
}

void CatchAllServer::stop() noexcept
{
    if (!running_.load()) {
        return;
    }

    running_.store(false);

    /*
     * Завдання стоїть у блокувальному recvfrom. shutdown() пробуджує його
     * помилкою, після чого воно саме закриває дескриптор і зникає.
     */
    socket_.shutdown();

    while (task_ != nullptr) {
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

void CatchAllServer::taskEntry(void *context) noexcept
{
    auto *self = static_cast<CatchAllServer *>(context);
    self->serve();

    self->socket_.reset();
    self->running_.store(false);
    self->task_ = nullptr;

    ESP_LOGI(kTag, "Завдання DNS завершено");
    vTaskDelete(nullptr);
}

void CatchAllServer::serve() noexcept
{
    std::array<std::uint8_t, kBufferSize> buffer{};

    while (running_.load()) {
        sockaddr_in client{};
        socklen_t clientLength = sizeof(client);

        const ssize_t received =
            ::recvfrom(socket_.get(), buffer.data(), buffer.size(), 0,
                       reinterpret_cast<sockaddr *>(&client), &clientLength);
        if (received < 0) {
            if (errno == EINTR) {
                continue;
            }
            if (running_.load()) {
                ESP_LOGE(kTag, "recvfrom: %d (%s)", errno, std::strerror(errno));
            }
            return;
        }

        const auto replyLength = buildResponse(
            buffer, static_cast<std::size_t>(received), answerIp_);
        if (!replyLength) {
            continue;  /* мовчимо: відповідати на брухт нема сенсу */
        }

        if (::sendto(socket_.get(), buffer.data(), *replyLength, 0,
                     reinterpret_cast<const sockaddr *>(&client), clientLength) < 0) {
            ESP_LOGW(kTag, "sendto: %d (%s)", errno, std::strerror(errno));
        }
    }
}

}  // namespace portal::dns
