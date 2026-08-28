#include <memory>
#include <vector>

class History {
  std::vector<std::unique_ptr<Command>> done_;    // виконані, ще не скасовані
  std::vector<std::unique_ptr<Command>> undone_;  // скасовані, чекають на redo
public:
  // виконати НОВУ дію
  void run(std::unique_ptr<Command> cmd) {
    cmd->execute();
    done_.push_back(std::move(cmd));
    undone_.clear();                     // ← інваріант: нова дія стирає redo-гілку
  }

  void undo() {
    if (done_.empty()) return;           // край: скасовувати нічого
    std::unique_ptr<Command> cmd = std::move(done_.back());
    done_.pop_back();
    cmd->undo();
    undone_.push_back(std::move(cmd));
  }

  void redo() {
    if (undone_.empty()) return;         // край: повторювати нічого
    std::unique_ptr<Command> cmd = std::move(undone_.back());
    undone_.pop_back();
    cmd->execute();
    done_.push_back(std::move(cmd));
  }

  bool canUndo() const { return !done_.empty(); }
  bool canRedo() const { return !undone_.empty(); }
};
