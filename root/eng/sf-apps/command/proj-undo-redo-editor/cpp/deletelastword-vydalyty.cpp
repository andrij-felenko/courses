class DeleteLastWord : public Command {
  TextDocument& doc_;
  std::size_t from_ = 0;        // звідки різали
  std::string removed_;         // що саме зрізали (запам'ятаємо в execute)
public:
  explicit DeleteLastWord(TextDocument& doc) : doc_(doc) {}

  void execute() override {
    from_ = doc_.lastWordStart();
    // remove повертає вирізане — ловимо його, поки воно не зникло назавжди
    removed_ = doc_.remove(from_, doc_.length());
  }

  void undo() override {
    // повертаємо зрізане рівно туди, звідки взяли
    doc_.insert(from_, removed_);
  }
};
