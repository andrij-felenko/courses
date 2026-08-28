#include <deque>

class PinnedCache {
    static constexpr std::size_t CAP = 64;               // скільки гарячих тримати
    std::deque<std::shared_ptr<const TreeKind>> hot_;     // СИЛЬНІ пінувальні посилання
public:
    void touch(std::shared_ptr<const TreeKind> k) {
        hot_.push_front(std::move(k));
        if (hot_.size() > CAP) hot_.pop_back();           // найхолодніший втрачає пін
    }
};
