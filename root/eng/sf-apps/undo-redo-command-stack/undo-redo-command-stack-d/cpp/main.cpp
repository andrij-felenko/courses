class History {
  std::vector<Step> steps_;
  int index_ = 0;        // скільки кроків застосовано
  int savedIndex_ = 0;   // індекс, на якому документ збережено
public:
  void markSaved() { savedIndex_ = index_; }
  bool isDirty() const { return index_ != savedIndex_; }

  // нова дія зрізає гілку повтору
  void push(Step step) {
    steps_.resize(index_);                          // усе після поточного — відрізано
    if (savedIndex_ > index_) savedIndex_ = -1;     // збереження було в зрізаному
    steps_.push_back(std::move(step));
    ++index_;
  }
};
