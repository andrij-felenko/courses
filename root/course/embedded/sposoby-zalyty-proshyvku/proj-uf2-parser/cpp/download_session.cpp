#include "download_session.hpp"

namespace uf2 {

bool isForeignSector(const AcceptError& e) noexcept
{
    const auto* parse = std::get_if<ParseError>(&e);
    return parse != nullptr && isForeignSector(*parse);
}

namespace {

std::string_view describeSession(SessionError e) noexcept
{
    switch (e) {
    case SessionError::BlockCountMismatch: return "різні numBlocks в одному образі";
    case SessionError::ImageTooLarge:      return "образ більший за бітову карту";
    case SessionError::AddressOutOfMap:    return "адреса поза картою секторів";
    case SessionError::EraseFailed:        return "збій стирання Flash";
    case SessionError::ProgramFailed:      return "збій запису Flash";
    }
    return "невідома відмова сеансу";
}

} // namespace

std::string_view describe(const AcceptError& e) noexcept
{
    return std::visit([](auto value) -> std::string_view {
        if constexpr (std::is_same_v<decltype(value), ParseError>) {
            return describe(value);
        } else {
            return describeSession(value);
        }
    }, e);
}

/*
 * Стирання «за першим дотиком». Наївне правило «стерти, коли адреса кратна
 * 4096» ламається саме через довільний порядок секторів: вирівняний блок може
 * приїхати останнім і знищити п'ятнадцять уже записаних сусідів. Тому кожен
 * 4-кілобайтний сектор стирається рівно один раз за сеанс.
 */
std::expected<void, SessionError>
DownloadSession::ensureErased(std::uint32_t address, std::uint32_t length) noexcept
{
    const std::uint32_t first = (address - flash_.start) / FlashSectorSize;
    const std::uint32_t last  = (address + length - 1 - flash_.start) / FlashSectorSize;

    for (std::uint32_t i = first; i <= last; ++i) {
        if (i >= MaxSectors) {
            return std::unexpected(SessionError::AddressOutOfMap);
        }
        if (erased_.test(i)) {
            continue;
        }
        if (!port::eraseSector(flash_.start + i * FlashSectorSize)) {
            return std::unexpected(SessionError::EraseFailed);
        }
        erased_.set(i);
    }
    return {};
}

// Повторний приїзд того самого блоку не рахується двічі.
void DownloadSession::markHandled(std::uint32_t index) noexcept
{
    if (!written_.test(index)) {
        written_.set(index);
        ++handledBlocks_;
    }
}

std::expected<DownloadSession::Progress, AcceptError>
DownloadSession::accept(std::span<const std::uint8_t> sector) noexcept
{
    const auto parsed = parseBlock(sector, familyId_, flash_);
    if (!parsed) {
        return std::unexpected(AcceptError{parsed.error()});
    }
    const BlockInfo& block = *parsed;

    if (block.totalBlocks > MaxBlocks) {
        return std::unexpected(AcceptError{SessionError::ImageTooLarge});
    }

    // Перший блок задає розмір образу. Інше numBlocks далі означає, що на диск
    // копіюють два різні файли .uf2 — змішувати їх в один образ не можна.
    if (totalBlocks_ == 0) {
        totalBlocks_ = block.totalBlocks;
    } else if (totalBlocks_ != block.totalBlocks) {
        return std::unexpected(AcceptError{SessionError::BlockCountMismatch});
    }

    // Порожній payload — блок не для Flash, але у numBlocks він порахований,
    // тож у карті його треба відмітити, інакше сеанс ніколи не завершиться.
    if (!block.payload.empty()) {
        if (auto erased = ensureErased(block.targetAddress,
                                       static_cast<std::uint32_t>(block.payload.size()));
            !erased) {
            return std::unexpected(AcceptError{erased.error()});
        }
        // Повторний запис безпечний: дані ті самі, а програмування NOR лише
        // скидає біти в нуль. Хост іноді пересилає сектор після таймауту.
        if (!port::program(block.targetAddress, block.payload)) {
            return std::unexpected(AcceptError{SessionError::ProgramFailed});
        }
    }

    markHandled(block.blockIndex);
    return progress();
}

DownloadSession::Progress DownloadSession::progress() const noexcept
{
    return Progress{.handled  = handledBlocks_,
                    .total    = totalBlocks_,
                    .complete = totalBlocks_ != 0 && handledBlocks_ == totalBlocks_};
}

} // namespace uf2
