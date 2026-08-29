#pragma once

#include <chrono>
#include <filesystem>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace genealogy {

using Timestamp = std::chrono::sys_seconds;

// Скільки плат довкола стику котушок вважаємо непевними: у тракті подавача
// лишається 10-20 компонентів, яких сканер живильника вже не бачив.
inline constexpr std::size_t kSpliceBoards = 20;

struct PartOrigin {
    std::string designator;   // C12, U4, R28
    std::string reel_uid;
    std::string lot_code;
    std::string date_code;
    bool uncertain{false};    // плата стоїть у зоні склейки стрічок
};

struct Board {
    std::string serial;
    std::string line;             // SMT-лінія
    std::string reflow_profile;   // термопрофіль печі
    Timestamp scanned{};          // сканування DataMatrix на вході лінії
    std::vector<PartOrigin> parts;
    bool failed{false};
    double ttf_hours{0.0};

    [[nodiscard]] const PartOrigin* part(std::string_view designator) const noexcept;
};

// Вікно життя котушки в живильнику: [from, to) на конкретній лінії.
struct FeederWindow {
    std::string line, designator, reel_uid, lot_code, date_code;
    Timestamp from{}, to{};
    bool spliced{false};          // перехід до наступної котушки зробили склейкою
};

class ProductionLog {
public:
    // mes.csv:     serial,smt_line,reflow_profile,scan_epoch
    // feeders.csv: smt_line,designator,reel_uid,lot_code,date_code,from_epoch,to_epoch,spliced
    // returns.csv: serial,ttf_hours,symptom
    // Кидає std::runtime_error із назвою файла й номером рядка.
    static ProductionLog load(const std::filesystem::path& mes,
                              const std::filesystem::path& feeders,
                              const std::filesystem::path& returns);

    void add_board(Board board) { boards_.push_back(std::move(board)); }
    void add_feeder(FeederWindow window) { feeders_.push_back(std::move(window)); }

    // Зшивання генеалогії: котушки, що стояли на лінії плати в мить сканування.
    void join();

    [[nodiscard]] std::span<const Board> boards() const noexcept { return boards_; }
    [[nodiscard]] std::size_t feeder_count() const noexcept { return feeders_.size(); }

private:
    void mark_splice_zones();

    std::vector<Board> boards_;
    std::vector<FeederWindow> feeders_;
};

}  // namespace genealogy
