// svid_sniffer.hpp - Ідіоматичний C++20 декодер протоколу SVID
#pragma once

#include <cstdint>
#include <cstddef>
#include <optional>
#include <span>
#include <string_view>

namespace svid {

enum class Command : uint8_t {
    SetVidFast  = 0x00,
    SetVidSlow  = 0x01,
    SetVidDecay = 0x02,
    SetReg      = 0x03,
    GetReg      = 0x04,
    SetOffset   = 0x07,
    Unknown     = 0x1F
};

enum class AckStatus : uint8_t {
    Ok   = 0x00,
    Nack = 0x01,
    Busy = 0x02
};

enum class State : uint8_t {
    Idle,
    Address,
    Command,
    Data,
    Parity,
    TurnAround,
    Ack,
    SlaveData,
    SlaveParity
};

struct Packet {
    uint8_t address{0};
    Command command{Command::Unknown};
    uint8_t masterData{0};
    bool masterParityOk{false};
    AckStatus slaveAck{AckStatus::Nack};
    uint8_t slaveData{0};
    bool slaveParityOk{false};
    uint32_t timestampUs{0};

    [[nodiscard]] double voltageVr12() const noexcept {
        if (masterData == 0x00 || masterData == 0xFF) return 0.0;
        return 0.245 + (static_cast<double>(masterData) * 0.005);
    }

    [[nodiscard]] double currentImon(double maxCurrentA) const noexcept {
        return (static_cast<double>(slaveData) / 255.0) * maxCurrentA;
    }

    [[nodiscard]] double temperatureTmon() const noexcept {
        return static_cast<double>(slaveData);
    }

    [[nodiscard]] double powerWatts(double maxCurrentA) const noexcept {
        return voltageVr12() * currentImon(maxCurrentA);
    }
};

class Decoder {
public:
    constexpr Decoder() noexcept = default;

    void reset() noexcept {
        state_ = State::Idle;
        bitIndex_ = 0;
        shiftReg_ = 0;
        onesCount_ = 0;
    }

    // Обробка одного такту SCLK/SDATA. Повертає декодований пакет при завершенні транзакції.
    [[nodiscard]] std::optional<Packet> step(bool sdata, uint32_t timestampUs) noexcept {
        switch (state_) {
        case State::Idle:
            if (!sdata) {
                state_ = State::Address;
                bitIndex_ = 0;
                shiftReg_ = 0;
                onesCount_ = 0;
                currentPkt_.timestampUs = timestampUs;
            }
            break;

        case State::Address:
            shiftReg_ = static_cast<uint16_t>((shiftReg_ << 1) | (sdata ? 1 : 0));
            if (sdata) ++onesCount_;
            if (++bitIndex_ == 4) {
                currentPkt_.address = static_cast<uint8_t>(shiftReg_ & 0x0F);
                state_ = State::Command;
                bitIndex_ = 0;
                shiftReg_ = 0;
            }
            break;

        case State::Command:
            shiftReg_ = static_cast<uint16_t>((shiftReg_ << 1) | (sdata ? 1 : 0));
            if (sdata) ++onesCount_;
            if (++bitIndex_ == 5) {
                currentPkt_.command = static_cast<Command>(shiftReg_ & 0x1F);
                state_ = State::Data;
                bitIndex_ = 0;
                shiftReg_ = 0;
            }
            break;

        case State::Data:
            shiftReg_ = static_cast<uint16_t>((shiftReg_ << 1) | (sdata ? 1 : 0));
            if (sdata) ++onesCount_;
            if (++bitIndex_ == 8) {
                currentPkt_.masterData = static_cast<uint8_t>(shiftReg_ & 0xFF);
                state_ = State::Parity;
            }
            break;

        case State::Parity:
            if (sdata) ++onesCount_;
            currentPkt_.masterParityOk = ((onesCount_ & 1) == 1);
            state_ = State::TurnAround;
            bitIndex_ = 0;
            break;

        case State::TurnAround:
            if (++bitIndex_ == 2) {
                state_ = State::Ack;
                bitIndex_ = 0;
                shiftReg_ = 0;
                onesCount_ = 0;
            }
            break;

        case State::Ack:
            shiftReg_ = static_cast<uint16_t>((shiftReg_ << 1) | (sdata ? 1 : 0));
            if (++bitIndex_ == 2) {
                currentPkt_.slaveAck = static_cast<AckStatus>(shiftReg_ & 0x03);
                if (currentPkt_.command == Command::GetReg) {
                    state_ = State::SlaveData;
                    bitIndex_ = 0;
                    shiftReg_ = 0;
                    onesCount_ = 0;
                } else {
                    state_ = State::Idle;
                    return currentPkt_;
                }
            }
            break;

        case State::SlaveData:
            shiftReg_ = static_cast<uint16_t>((shiftReg_ << 1) | (sdata ? 1 : 0));
            if (sdata) ++onesCount_;
            if (++bitIndex_ == 8) {
                currentPkt_.slaveData = static_cast<uint8_t>(shiftReg_ & 0xFF);
                state_ = State::SlaveParity;
            }
            break;

        case State::SlaveParity:
            if (sdata) ++onesCount_;
            currentPkt_.slaveParityOk = ((onesCount_ & 1) == 1);
            state_ = State::Idle;
            return currentPkt_;
        }

        return std::nullopt;
    }

private:
    State state_{State::Idle};
    uint8_t bitIndex_{0};
    uint16_t shiftReg_{0};
    uint8_t onesCount_{0};
    Packet currentPkt_{};
};

} // namespace svid
