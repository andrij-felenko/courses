class MacroCommand : public Command {
  std::vector<std::unique_ptr<Command>> commands_;
public:
  explicit MacroCommand(std::vector<std::unique_ptr<Command>> commands)
    : commands_(std::move(commands)) {}

  void execute() override {
    for (auto& c : commands_) c->execute();              // усі вперед, по порядку
  }

  void undo() override {
    for (auto it = commands_.rbegin(); it != commands_.rend(); ++it)
      (*it)->undo();                                     // ...і назад у ЗВОРОТНОМУ
  }
};
