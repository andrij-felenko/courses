#include <string>

class TextDocument {
  std::string text_;                        // UTF-8; індекси — байтові зсуви
public:
  const std::string& content() const { return text_; }
  std::size_t length() const { return text_.size(); }

  // вставити рядок у позицію pos (0 ≤ pos ≤ length)
  void insert(std::size_t pos, const std::string& s) {
    text_.insert(pos, s);
  }

  // вирізати [from, to) і повернути вирізане (щоб команда його запам'ятала)
  std::string remove(std::size_t from, std::size_t to) {
    std::string cut = text_.substr(from, to - from);
    text_.erase(from, to - from);
    return cut;
  }

  // межа останнього слова: індекс, з якого воно починається
  std::size_t lastWordStart() const {
    std::size_t end = text_.find_last_not_of(" \t\n\r");  // без хвостових пробілів
    if (end == std::string::npos) return 0;               // самі пробіли
    std::size_t sp = text_.rfind(' ', end);
    return sp == std::string::npos ? 0 : sp + 1;          // немає пробілу → від початку
  }
};
