class AddText : public Command {
  TextDocument& doc_;
  std::size_t pos_;
  std::string text_;
public:
  AddText(TextDocument& doc, std::size_t pos, std::string text)
    : doc_(doc), pos_(pos), text_(std::move(text)) {}

  void execute() override {
    doc_.insert(pos_, text_);
  }

  void undo() override {
    // вставили text у pos → щоб відкотити, вирізаємо [pos, pos + text.size())
    doc_.remove(pos_, pos_ + text_.size());
  }
};
