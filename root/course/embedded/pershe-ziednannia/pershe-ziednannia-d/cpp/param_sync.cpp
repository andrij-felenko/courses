#include "param_sync.h"

#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>

namespace {

// CRC32 (IEEE, поліном 0xEDB88320) без таблиці — для звіряння локального кеша.
std::uint32_t crc32(const std::string& data) {
    std::uint32_t crc = 0xFFFFFFFFu;
    for (unsigned char byte : data) {
        crc ^= byte;
        for (int i = 0; i < 8; ++i) {
            crc = (crc >> 1) ^ (0xEDB88320u & (0u - (crc & 1u)));
        }
    }
    return ~crc;
}

}  // namespace

ParamSync::ParamSync(SerialLink& link, std::uint8_t gcs_sysid, std::uint8_t gcs_compid)
    : link_(link), gcs_sysid_(gcs_sysid), gcs_compid_(gcs_compid) {}

void ParamSync::start(std::uint8_t tsys, std::uint8_t tcomp, Clock::time_point now) {
    tsys_ = tsys;
    tcomp_ = tcomp;
    count_ = 0;
    received_ = 0;
    got_.clear();
    values_.clear();
    cursor_ = 0;
    rounds_ = 0;
    list_attempts_ = 0;
    state_ = State::WaitList;
    sendRequestList(now);
}

void ParamSync::sendRequestList(Clock::time_point now) {
    mavlink_message_t m;
    mavlink_msg_param_request_list_pack(gcs_sysid_, gcs_compid_, &m, tsys_, tcomp_);
    link_.send(m);
    ++list_attempts_;
    last_tx_ = now;
    last_rx_ = now;
    std::cout << "[2/5] PARAM_REQUEST_LIST → чекаємо потік PARAM_VALUE\n";
}

void ParamSync::onMessage(const mavlink_message_t& msg, Clock::time_point now) {
    if (state_ != State::WaitList && state_ != State::Recovering) return;
    if (msg.msgid != MAVLINK_MSG_ID_PARAM_VALUE) return;
    if (msg.sysid != tsys_ || msg.compid != tcomp_) return;

    mavlink_param_value_t pv;
    mavlink_msg_param_value_decode(&msg, &pv);
    last_rx_ = now;

    if (got_.empty()) {
        if (pv.param_count == 0) {  // борт без параметрів — теоретично можливо
            state_ = State::Done;
            std::cout << "[2/5] автопілот повідомив param_count = 0\n";
            return;
        }
        count_ = pv.param_count;
        got_.assign(count_, false);
        state_ = State::Recovering;
        std::cout << "[2/5] param_count = " << count_ << ", виділено бітову маску індексів\n";
    }

    // param_index == 0xFFFF означає відповідь на запит за іменем: у масці їй місця немає.
    if (pv.param_index == UINT16_MAX || pv.param_index >= count_) return;

    char name[17] = {};
    std::memcpy(name, pv.param_id, 16);  // рівно 16 символів без нуля — теж легальний варіант
    values_[name] = pv.param_value;

    if (!got_[pv.param_index]) {
        got_[pv.param_index] = true;
        if (++received_ % 200 == 0) {
            std::cout << "      прийнято " << received_ << " / " << count_ << "\n";
        }
    }
    if (received_ == count_) finish();
}

void ParamSync::tick(Clock::time_point now) {
    if (state_ != State::WaitList && state_ != State::Recovering) return;

    if (state_ == State::WaitList) {
        if (now - last_tx_ < kListTimeout) return;
        if (list_attempts_ >= 3) {
            std::cout << "[!] автопілот не відповів на PARAM_REQUEST_LIST\n";
            state_ = State::Failed;
            return;
        }
        sendRequestList(now);
        return;
    }

    // Дозапити починаємо лише коли потік стих: інакше ми самі собі створимо
    // колізію в напівдуплексному ефірі.
    if (now - last_rx_ < kSilence) return;
    if (now - last_tx_ < pacing_) return;
    requestMissing(now);
}

void ParamSync::requestMissing(Clock::time_point now) {
    std::size_t sent = 0;
    for (std::size_t scanned = 0; scanned < got_.size() && sent < kBatch; ++scanned) {
        const std::size_t idx = (cursor_ + scanned) % got_.size();
        if (got_[idx]) continue;

        mavlink_message_t m;
        // Порожнє ім'я плюс індекс — адресний дозапит саме цього номера.
        mavlink_msg_param_request_read_pack(gcs_sysid_, gcs_compid_, &m, tsys_, tcomp_, "",
                                            static_cast<std::int16_t>(idx));
        link_.send(m);
        cursor_ = idx + 1;
        ++sent;
    }

    if (sent == 0) {  // дірок не лишилось, хоча лічильник ще не зійшовся
        finish();
        return;
    }
    last_tx_ = now;
    if (++rounds_ == 1 || rounds_ % 5 == 0) {
        std::cout << "      дірки в списку: " << (count_ - received_)
                  << ", дозапит пачкою по " << sent << " (раунд " << rounds_ << ")\n";
    }
    if (rounds_ > kMaxRounds) {
        std::cout << "[!] " << (count_ - received_)
                  << " параметрів не вичитано за " << kMaxRounds << " раундів — лінк надто поганий\n";
        state_ = State::Failed;
    }
}

void ParamSync::finish() {
    state_ = State::Done;
    std::cout << "[2/5] вичитано " << values_.size() << " параметрів\n";
    checkCache();
}

void ParamSync::checkCache() {
    // Стандартного повідомлення «дай хеш параметрів» у MAVLink немає, тож хеш
    // рахує сама станція: збіг із кешем означає, що збережені налаштування чинні
    // і всі похідні (діапазони повзунків, назви каналів) можна не перебудовувати.
    std::ostringstream blob;
    blob << std::setprecision(9);
    for (const auto& [name, value] : values_) blob << name << '=' << value << '\n';
    const std::uint32_t crc = crc32(blob.str());

    const std::string path = "params-" + std::to_string(tsys_) + ".cache";
    std::uint32_t cached = 0;
    {
        std::ifstream in(path);
        if (in >> std::hex >> cached && cached == crc) {
            std::cout << "[2/5] кеш параметрів чинний (CRC32 0x" << std::hex << crc << std::dec
                      << ")\n";
            return;
        }
    }

    std::ofstream out(path, std::ios::trunc);
    if (!out) {
        std::cout << "[!] кеш параметрів не записався: " << path << "\n";
        return;
    }
    out << std::hex << crc << std::dec << '\n' << blob.str();
    std::cout << "[2/5] кеш параметрів оновлено (CRC32 0x" << std::hex << crc << std::dec << ")\n";
}
