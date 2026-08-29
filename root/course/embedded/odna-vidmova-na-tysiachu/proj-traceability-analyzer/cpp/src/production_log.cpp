#include "production_log.hpp"

#include <algorithm>
#include <cctype>
#include <charconv>
#include <format>
#include <fstream>
#include <functional>
#include <iostream>
#include <ranges>
#include <stdexcept>
#include <tuple>
#include <unordered_map>

namespace genealogy {
namespace {

std::string_view trim(std::string_view s) {
    while (!s.empty() && std::isspace(static_cast<unsigned char>(s.front()))) s.remove_prefix(1);
    while (!s.empty() && std::isspace(static_cast<unsigned char>(s.back()))) s.remove_suffix(1);
    return s;
}

std::vector<std::string_view> split(std::string_view line) {
    std::vector<std::string_view> fields;
    while (true) {
        const auto comma = line.find(',');
        fields.push_back(trim(line.substr(0, comma)));
        if (comma == std::string_view::npos) break;
        line.remove_prefix(comma + 1);
    }
    return fields;
}

template <class T>
T parse_number(std::string_view text, std::string_view field) {
    T value{};
    const auto* last = text.data() + text.size();
    const auto [ptr, ec] = std::from_chars(text.data(), last, value);
    if (ec != std::errc{} || ptr != last)
        throw std::runtime_error(std::format("поле {} = '{}' не є числом", field, text));
    return value;
}

using RowHandler = std::function<void(std::span<const std::string_view>)>;

void for_each_row(const std::filesystem::path& path, std::string_view header_hint,
                  const RowHandler& handler) {
    std::ifstream in(path);
    if (!in)
        throw std::runtime_error(std::format("{}: не вдалося відкрити файл", path.string()));

    std::string raw;
    std::size_t lineno = 0;
    while (std::getline(in, raw)) {
        ++lineno;
        if (!raw.empty() && raw.back() == '\r') raw.pop_back();
        const auto text = trim(raw);
        if (text.empty() || text.front() == '#') continue;
        if (lineno == 1 && text.starts_with(header_hint)) continue;   // шапка

        const auto fields = split(text);
        try {
            handler(fields);
        } catch (const std::exception& e) {
            throw std::runtime_error(std::format("{}:{}: {}", path.string(), lineno, e.what()));
        }
    }
    if (in.bad())
        throw std::runtime_error(std::format("{}: помилка читання", path.string()));
}

Timestamp seconds_to_ts(long long epoch) {
    return Timestamp{std::chrono::seconds{epoch}};
}

}  // namespace

const PartOrigin* Board::part(std::string_view designator) const noexcept {
    const auto it = std::ranges::find(parts, designator, &PartOrigin::designator);
    return it == parts.end() ? nullptr : &*it;
}

ProductionLog ProductionLog::load(const std::filesystem::path& mes,
                                  const std::filesystem::path& feeders,
                                  const std::filesystem::path& returns) {
    ProductionLog log;

    for_each_row(mes, "serial", [&](std::span<const std::string_view> f) {
        if (f.size() < 4)
            throw std::runtime_error("очікую serial,smt_line,reflow_profile,scan_epoch");
        if (f[0].empty()) throw std::runtime_error("порожній серійний номер");
        Board board;
        board.serial = std::string{f[0]};
        board.line = std::string{f[1]};
        board.reflow_profile = std::string{f[2]};
        board.scanned = seconds_to_ts(parse_number<long long>(f[3], "scan_epoch"));
        log.boards_.push_back(std::move(board));
    });

    for_each_row(feeders, "smt_line", [&](std::span<const std::string_view> f) {
        if (f.size() < 7)
            throw std::runtime_error("очікую smt_line,designator,reel_uid,lot_code,"
                                     "date_code,from_epoch,to_epoch[,spliced]");
        FeederWindow w;
        w.line = std::string{f[0]};
        w.designator = std::string{f[1]};
        w.reel_uid = std::string{f[2]};
        w.lot_code = std::string{f[3]};
        w.date_code = std::string{f[4]};
        w.from = seconds_to_ts(parse_number<long long>(f[5], "from_epoch"));
        w.to = seconds_to_ts(parse_number<long long>(f[6], "to_epoch"));
        if (w.to <= w.from)
            throw std::runtime_error(std::format("порожнє вікно котушки {}", w.reel_uid));
        w.spliced = f.size() > 7 && (f[7] == "1" || f[7] == "y" || f[7] == "Y");
        log.feeders_.push_back(std::move(w));
    });

    std::unordered_map<std::string_view, Board*> index;
    index.reserve(log.boards_.size());
    for (auto& board : log.boards_) index.emplace(board.serial, &board);

    std::size_t unknown = 0;
    for_each_row(returns, "serial", [&](std::span<const std::string_view> f) {
        if (f.empty()) throw std::runtime_error("очікую serial,ttf_hours[,symptom]");
        const auto it = index.find(f[0]);
        if (it == index.end()) {
            ++unknown;   // повернення з чужого випуску не привід валити аналіз
            return;
        }
        it->second->failed = true;
        if (f.size() > 1 && !f[1].empty())
            it->second->ttf_hours = parse_number<double>(f[1], "ttf_hours");
    });
    if (unknown > 0)
        std::cerr << std::format("Попередження: {} рекламацій без плати в журналі MES\n", unknown);

    return log;
}

void ProductionLog::join() {
    for (auto& board : boards_) {
        board.parts.clear();
        for (const auto& w : feeders_) {
            if (w.line != board.line || board.scanned < w.from || board.scanned >= w.to) continue;
            const auto it = std::ranges::find(board.parts, w.designator, &PartOrigin::designator);
            if (it != board.parts.end()) {
                it->uncertain = true;   // вікна на той самий десігнатор перекрилися
                continue;
            }
            board.parts.push_back(PartOrigin{w.designator, w.reel_uid, w.lot_code, w.date_code, false});
        }
    }
    mark_splice_zones();
}

void ProductionLog::mark_splice_zones() {
    if (boards_.empty()) return;

    std::vector<Board*> index;
    index.reserve(boards_.size());
    for (auto& board : boards_) index.push_back(&board);
    std::ranges::sort(index, [](const Board* x, const Board* y) {
        return std::tie(x->line, x->scanned) < std::tie(y->line, y->scanned);
    });

    constexpr auto by_line = [](const Board* b) -> const std::string& { return b->line; };
    constexpr auto by_time = [](const Board* b) { return b->scanned; };

    for (const auto& w : feeders_) {
        if (!w.spliced) continue;
        auto same_line = std::ranges::equal_range(index, w.line, std::less{}, by_line);
        if (same_line.empty()) continue;

        const auto boundary = std::ranges::lower_bound(same_line, w.to, std::less{}, by_time);
        const auto span = static_cast<std::ptrdiff_t>(kSpliceBoards);
        const auto first = boundary - std::min(span, boundary - same_line.begin());
        const auto last = boundary + std::min(span, same_line.end() - boundary);

        for (auto it = first; it != last; ++it) {
            auto& parts = (*it)->parts;
            const auto part = std::ranges::find(parts, w.designator, &PartOrigin::designator);
            if (part != parts.end()) part->uncertain = true;
        }
    }
}

}  // namespace genealogy
