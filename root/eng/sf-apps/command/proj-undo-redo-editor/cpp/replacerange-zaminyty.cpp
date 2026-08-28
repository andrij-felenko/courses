class ReplaceRange : public Command {
  TextDocument& doc_;
  std::size_t from_, to_;
  std::string newText_;
  std::string oldText_;         // що стояло в [from, to) до заміни
public:
  ReplaceRange(TextDocument& doc, std::size_t from, std::size_t to, std::string newText)
    : doc_(doc), from_(from), to_(to), newText_(std::move(newText)) {}

  void execute() override {
    // 1) вирізали старе — і одразу впіймали його в oldText
    oldText_ = doc_.remove(from_, to_);
    // 2) вставили нове на те саме місце
    doc_.insert(from_, newText_);
  }

  void undo() override {
    // дзеркально й у зворотному порядку:
    // 1) прибрати нове (воно завдовжки newText, стоїть від from)
    doc_.remove(from_, from_ + newText_.size());
    // 2) повернути старе на місце
    doc_.insert(from_, oldText_);
  }
};
