#include "cfg/manager.hpp"

#include <format>

namespace cfg {

PayloadV2 Manager::factory_defaults() noexcept
{
    PayloadV2 cfg{};
    assign(cfg.wifi_ssid, "Factory_AP");
    assign(cfg.wifi_pass, "SecretPass123");
    assign(cfg.broker_host, "mqtt.iot-cloud.internal");
    cfg.broker_port       = 8883;
    cfg.tls_enable        = 1;
    cfg.report_interval_s = 60;
    cfg.conn_timeout_s    = 180;
    return cfg;
}

// Крок міграції v1 → v2: переносимо те, що було, і дораховуємо те, чого не було.
PayloadV2 Manager::migrate_v1_to_v2(const PayloadV1& v1)
{
    PayloadV2 v2{};
    assign(v2.wifi_ssid, view(v1.wifi_ssid));
    assign(v2.wifi_pass, view(v1.wifi_pass));

    // v1 знала лише адресу IPv4 — розгортаємо її в ім'я хоста нової схеми.
    assign(v2.broker_host, std::format("{}.{}.{}.{}",
                                       v1.broker_ip[0], v1.broker_ip[1],
                                       v1.broker_ip[2], v1.broker_ip[3]));

    // Полів, яких у старому записі немає, з повітря не візьмеш —
    // ставимо безпечні дефолти, а не нулі.
    v2.broker_port = 8883;
    v2.tls_enable  = 1;
    v2.report_interval_s = (v1.report_interval_s >= 1 && v1.report_interval_s <= kReportMaxS)
                           ? v1.report_interval_s : 60;
    v2.conn_timeout_s = v2.report_interval_s * 3;
    return v2;
}

std::expected<void, Error> Manager::validate(const PayloadV2& cfg) noexcept
{
    // Структура приїхала з мережі або з Flash: рядки можуть бути без нуля.
    if (!terminated(cfg.wifi_ssid) || !terminated(cfg.wifi_pass) || !terminated(cfg.broker_host)) {
        return std::unexpected(Error::FieldNotTerminated);
    }
    if (view(cfg.wifi_ssid).empty()) {
        return std::unexpected(Error::EmptySsid);
    }
    if (view(cfg.broker_host).empty()) {
        return std::unexpected(Error::EmptyHost);
    }
    if (cfg.broker_port == 0) {
        return std::unexpected(Error::BadPort);
    }
    if (cfg.tls_enable > 1) {
        return std::unexpected(Error::TlsFlagInvalid);
    }
    if (cfg.report_interval_s == 0 || cfg.report_interval_s > kReportMaxS) {
        return std::unexpected(Error::BadInterval);
    }
    // Міжпольове правило: не можна оголошувати розрив зв'язку раніше, ніж пристрій
    // узагалі мав нагоду вийти в ефір із черговим звітом.
    if (cfg.conn_timeout_s <= cfg.report_interval_s) {
        return std::unexpected(Error::TimeoutTooShort);
    }
    return {};
}

std::expected<Header, Error> Manager::valid_header(std::size_t slot) const noexcept
{
    const auto sector = flash_.read(slot);
    const auto hdr = read_object<Header>(sector, 0);
    if (!hdr || hdr->magic != kMagic) {
        return std::unexpected(Error::NoValidRecord);   // сектор стертий або запис не дописано
    }
    if (hdr->payload_len == 0 || hdr->payload_len > sector.size() - sizeof(Header)) {
        return std::unexpected(Error::BadPayloadSize);
    }
    if (crc32(sector.subspan(sizeof(Header), hdr->payload_len)) != hdr->crc32_value) {
        return std::unexpected(Error::NoValidRecord);
    }
    return *hdr;
}

// Покроковий підйом запису до поточної схеми: кожне нове покоління додає сюди
// рівно один крок, тому прилад може перестрибнути кілька версій прошивки одразу.
std::expected<PayloadV2, Error> Manager::decode(std::size_t slot, const Header& hdr) const
{
    const auto sector = flash_.read(slot);

    if (hdr.schema_version == kSchemaV1) {
        if (hdr.payload_len != sizeof(PayloadV1)) {
            return std::unexpected(Error::BadPayloadSize);
        }
        const auto v1 = read_object<PayloadV1>(sector, sizeof(Header));
        if (!v1) {
            return std::unexpected(Error::BadPayloadSize);
        }
        return migrate_v1_to_v2(*v1);   // наступний крок ланцюга стане саме тут
    }
    if (hdr.schema_version == kSchemaCurrent) {
        if (hdr.payload_len != sizeof(PayloadV2)) {
            return std::unexpected(Error::BadPayloadSize);
        }
        const auto v2 = read_object<PayloadV2>(sector, sizeof(Header));
        if (!v2) {
            return std::unexpected(Error::BadPayloadSize);
        }
        return *v2;
    }
    return std::unexpected(Error::UnknownSchema);   // прошивку відкотили назад
}

// Ping-Pong: пишемо завжди в неактивний сектор і лише потім оголошуємо його активним.
std::expected<void, Error> Manager::write_record(const PayloadV2& cfg, std::uint32_t seq) noexcept
{
    const std::size_t target = active_slot_ ^ 1U;

    const Header hdr{
        .magic           = kMagic,
        .schema_version  = kSchemaCurrent,
        .flags           = 0,
        .sequence_number = seq,
        .payload_len     = static_cast<std::uint16_t>(sizeof(PayloadV2)),
        .reserved        = 0,
        .crc32_value     = crc32(raw_bytes(cfg)),
    };

    flash_.erase(target);
    if (auto written = flash_.program(target, sizeof(Header), raw_bytes(cfg)); !written) {
        return written;
    }
    // Заголовок — останнім. Обрив живлення до цієї миті лишає сектор без магії,
    // тобто невидимим для читача, а старий сектор і далі активний.
    if (auto written = flash_.program(target, 0, raw_bytes(hdr)); !written) {
        return written;
    }

    // Звірка читанням: зношений сектор міг не догасити біти.
    const auto back = valid_header(target);
    if (!back || back->crc32_value != hdr.crc32_value || back->sequence_number != seq) {
        return std::unexpected(Error::FlashVerifyFailed);
    }

    active_slot_ = target;
    last_seq_    = seq;
    return {};
}

std::expected<void, Error> Manager::initialize()
{
    // Викликається до старту задач, але блокування тут безкоштовне — беремо.
    const std::lock_guard guard{mtx_};

    std::array<std::optional<Header>, Flash::kSlots> headers{};
    std::uint32_t highest = 0;
    for (std::size_t slot = 0; slot < Flash::kSlots; ++slot) {
        if (auto hdr = valid_header(slot)) {
            headers[slot] = *hdr;
            highest = std::max(highest, hdr->sequence_number);
        }
    }

    // Спершу найсвіжіше покоління; якщо воно не читається — старіше.
    std::array<std::size_t, Flash::kSlots> order{0, 1};
    if (headers[1] && (!headers[0] || headers[1]->sequence_number > headers[0]->sequence_number)) {
        order = {1, 0};
    }

    for (const std::size_t slot : order) {
        if (!headers[slot]) {
            continue;
        }
        const auto decoded = decode(slot, *headers[slot]);
        if (!decoded) {
            continue;
        }
        // Мігрований запис проходить ту саму перевірку, що й кандидат із мережі.
        if (!validate(*decoded)) {
            continue;
        }

        active_config_ = *decoded;
        live_.store(&active_config_, std::memory_order_release);
        active_slot_ = slot;
        last_seq_    = headers[slot]->sequence_number;
        trial_running_.store(false, std::memory_order_relaxed);
        trial_left_s_ = 0;

        if (headers[slot]->schema_version != kSchemaCurrent) {
            // Мігровану структуру одразу фіксуємо в сусідньому секторі:
            // наступний старт уже не мігруватиме.
            return write_record(active_config_, last_seq_ + 1);
        }
        return {};
    }

    active_config_ = factory_defaults();
    live_.store(&active_config_, std::memory_order_release);
    trial_running_.store(false, std::memory_order_relaxed);
    trial_left_s_ = 0;
    active_slot_  = 1;   // щоб перший запис ліг у Slot A
    return write_record(active_config_, highest + 1);
}

std::expected<void, Error> Manager::start_trial(const PayloadV2& candidate, std::uint32_t timeout_s)
{
    if (auto ok = validate(candidate); !ok) {
        return ok;
    }

    const std::lock_guard guard{mtx_};
    if (trial_running_.load(std::memory_order_relaxed)) {
        return std::unexpected(Error::TrialActive);
    }

    candidate_config_ = candidate;
    // Стек починає працювати з кандидатом; active_config_ лишається цілим —
    // саме тому відкат нічого не відновлює, а лише повертає вказівник.
    live_.store(&candidate_config_, std::memory_order_release);
    trial_running_.store(true, std::memory_order_relaxed);
    trial_left_s_ = timeout_s;
    return {};
}

void Manager::rollback_locked() noexcept
{
    live_.store(&active_config_, std::memory_order_release);
    trial_running_.store(false, std::memory_order_relaxed);
    trial_left_s_ = 0;
}

std::expected<void, Error> Manager::confirm_commit()
{
    const std::lock_guard guard{mtx_};
    if (!trial_running_.load(std::memory_order_relaxed)) {
        return std::unexpected(Error::NoTrial);
    }

    // Спершу Flash. Якщо сектор не взяв запис — відкочуємось, а не вдаємо успіх:
    // інакше після перезавантаження прилад опинився б на старому профілі,
    // думаючи, що працює на новому.
    if (auto written = write_record(candidate_config_, last_seq_ + 1); !written) {
        rollback_locked();
        return written;
    }

    // Читачі поки тримають кандидата, тож переписувати active_config_ безпечно:
    // ніхто не бачить його наполовину заміненим.
    active_config_ = candidate_config_;
    live_.store(&active_config_, std::memory_order_release);
    trial_running_.store(false, std::memory_order_relaxed);
    trial_left_s_ = 0;
    return {};
}

void Manager::rollback() noexcept
{
    const std::lock_guard guard{mtx_};
    rollback_locked();
}

void Manager::tick_1hz() noexcept
{
    const std::lock_guard guard{mtx_};
    if (trial_running_.load(std::memory_order_relaxed) && trial_left_s_ > 0) {
        if (--trial_left_s_ == 0) {
            rollback_locked();   // підтвердження не надійшло
        }
    }
}

std::uint32_t Manager::seconds_left() const noexcept
{
    const std::lock_guard guard{mtx_};
    return trial_left_s_;
}

}  // namespace cfg
