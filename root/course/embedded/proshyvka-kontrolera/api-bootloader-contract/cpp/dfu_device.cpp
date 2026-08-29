#include "dfu_device.hpp"

#include <algorithm>

#include "boot_trigger.hpp"

namespace fc::dfu {
namespace {

template <class... Ts>
struct overloaded : Ts... { using Ts::operator()...; };

constexpr std::chrono::milliseconds kWritePoll{5};
constexpr std::chrono::milliseconds kManifestPoll{500};

// Відповідь на DFU_UPLOAD із wBlockNum = 0: перелік підтриманих команд DfuSe.
constexpr std::array<std::byte, 3> kSupportedCommands{
    std::byte{0x00},  // Get Commands
    std::byte{dfuse::kSetAddress},
    std::byte{dfuse::kErase},
};

}  // namespace

std::unexpected<Status> Device::fail(Status status) noexcept
{
    status_ = status;
    state_ = State::Error;
    pending_ = std::monostate{};
    return std::unexpected(status);
}

std::expected<Device::Reply, Status> Device::dnload(std::uint16_t block,
                                                    std::span<const std::byte> data)
{
    if (state_ != State::DfuIdle && state_ != State::DnloadIdle) {
        return fail(Status::ErrStalledPkt);
    }

    // Блок нульової довжини = кінець образу, далі фіналізація.
    if (data.empty()) {
        pending_ = ManifestOp{};
        poll_timeout_ = kManifestPoll;
        state_ = State::ManifestSync;
        return Reply{};
    }

    if (block == 0) {
        const auto command = dfuse::parse(data);
        if (!command) {
            return fail(command.error());
        }

        const auto applied = std::visit(overloaded{
            [this](const dfuse::SetAddress& cmd) -> std::expected<void, Status> {
                // Адресу судимо тут: хост має дізнатись про промах з першого GETSTATUS.
                if (!flash::sector_at(cmd.address)) {
                    return std::unexpected(Status::ErrAddress);
                }
                address_pointer_ = cmd.address;
                pending_ = std::monostate{};
                poll_timeout_ = std::chrono::milliseconds{0};
                return {};
            },
            [this](const dfuse::EraseSector& cmd) -> std::expected<void, Status> {
                const auto sector = flash::sector_at(cmd.address);
                if (!sector) {
                    return std::unexpected(Status::ErrAddress);
                }
                pending_ = EraseSectorOp{sector->address};
                poll_timeout_ = flash::erase_timeout(*sector);
                return {};
            },
            [this](const dfuse::EraseApplication&) -> std::expected<void, Status> {
                pending_ = EraseApplicationOp{};
                poll_timeout_ = flash::application_erase_timeout();
                return {};
            }}, *command);

        if (!applied) {
            return fail(applied.error());
        }
        state_ = State::DnloadSync;
        return Reply{};
    }

    if (block == 1) {
        return fail(Status::ErrStalledPkt);  // номер зарезервовано специфікацією
    }
    if (data.size() > kTransferSize) {
        return fail(Status::ErrStalledPkt);
    }

    // Адреса рахується від покажчика: перший блок даних має номер 2.
    const std::uint32_t address =
        address_pointer_ + (static_cast<std::uint32_t>(block) - 2u) * kTransferSize;
    if (!flash::in_application(address, data.size())) {
        return fail(Status::ErrAddress);
    }

    std::ranges::copy(data, buffer_.begin());
    pending_ = WriteOp{address, data.size()};
    poll_timeout_ = kWritePoll;
    state_ = State::DnloadSync;
    return Reply{};
}

std::expected<Device::Reply, Status> Device::upload(std::uint16_t block, std::uint16_t length)
{
    if (state_ != State::DfuIdle && state_ != State::UploadIdle) {
        return fail(Status::ErrStalledPkt);
    }

    if (block == 0) {
        state_ = State::DfuIdle;
        return Reply{kSupportedCommands};
    }
    if (block == 1 || length == 0) {
        return fail(Status::ErrStalledPkt);
    }

    const std::uint32_t address =
        address_pointer_ + (static_cast<std::uint32_t>(block) - 2u) * kTransferSize;
    const std::size_t want = std::min<std::size_t>(length, kTransferSize);
    const auto memory = flash::read(address, want);
    if (memory.empty()) {
        return fail(Status::ErrAddress);
    }

    state_ = State::UploadIdle;
    return memory;
}

std::expected<Device::Reply, Status> Device::get_status()
{
    StatusResponse response{.status = status_,
                            .poll_timeout = std::chrono::milliseconds{0},
                            .state = state_,
                            .string_index = 0};

    if (state_ == State::DnloadSync) {
        if (std::holds_alternative<std::monostate>(pending_)) {
            // Set Address Pointer нічого не пише — синхронізація миттєва.
            state_ = State::DnloadIdle;
            response.state = State::DnloadIdle;
        } else {
            state_ = State::DnBusy;
            response.state = State::DnBusy;
            response.poll_timeout = poll_timeout_;
        }
    } else if (state_ == State::ManifestSync) {
        state_ = State::Manifest;
        response.state = State::Manifest;
        response.poll_timeout = poll_timeout_;
    }

    reply_ = response.to_bytes();
    return Reply{reply_};
}

std::expected<Device::Reply, Status> Device::control_request(
    Request request, std::uint16_t block, std::uint16_t length,
    std::span<const std::byte> data)
{
    switch (request) {
    case Request::Detach:
        // У завантажувачі DETACH безглуздий: ми вже тут. Цей запит обробляє
        // польотна прошивка через boot::handle_detach().
        return fail(Status::ErrStalledPkt);

    case Request::Dnload:
        return dnload(block, data);

    case Request::Upload:
        return upload(block, length);

    case Request::GetStatus:
        return get_status();

    case Request::ClrStatus:
        if (state_ != State::Error) {
            return fail(Status::ErrStalledPkt);
        }
        status_ = Status::Ok;
        state_ = State::DfuIdle;
        return Reply{};

    case Request::GetState:
        reply_[0] = static_cast<std::byte>(state_);
        return Reply{reply_}.first(1);

    case Request::Abort:
        if (state_ == State::Error) {
            return fail(Status::ErrStalledPkt);
        }
        pending_ = std::monostate{};
        state_ = State::DfuIdle;
        return Reply{};
    }

    return fail(Status::ErrStalledPkt);
}

void Device::poll()
{
    if (state_ == State::DnBusy) {
        flash::Controller flash_ctl;  // доки живий — пам'ять відкрита на запис
        const auto result = std::visit(overloaded{
            [](std::monostate) -> std::expected<void, Status> {
                return std::unexpected(Status::ErrUnknown);
            },
            [&](const WriteOp& op) -> std::expected<void, Status> {
                return flash_ctl.program(op.address, std::span{buffer_}.first(op.length));
            },
            [&](const EraseSectorOp& op) -> std::expected<void, Status> {
                return flash_ctl.erase(op.address);
            },
            [&](const EraseApplicationOp&) -> std::expected<void, Status> {
                return flash_ctl.erase_application();
            },
            [](const ManifestOp&) -> std::expected<void, Status> {
                return std::unexpected(Status::ErrUnknown);
            }}, pending_);

        pending_ = std::monostate{};
        if (!result) {
            static_cast<void>(fail(result.error()));
            return;
        }
        state_ = State::DnloadIdle;
        return;
    }

    if (state_ == State::Manifest) {
        pending_ = std::monostate{};
        if (!flash::application_image_valid()) {
            // Образ побитий: у застосунок не стрибаємо, лишаємось у DFU.
            static_cast<void>(fail(Status::ErrFirmware));
            return;
        }
        // bitManifestationTolerant = 0 — далі лише через скидання.
        state_ = State::ManifestWaitReset;
        boot::system_reset();
    }
}

}  // namespace fc::dfu
