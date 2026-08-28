// Зсув небажаних значень у кінець діапазону
template <class ForwardIt, class T>
ForwardIt remove(ForwardIt first, ForwardIt last, const T& value);

template <class ForwardIt, class UnaryPredicate>
ForwardIt remove_if(ForwardIt first, ForwardIt last, UnaryPredicate p);

// Вилучення послідовних однаковим елементів у впорядкованому масиві
template <class ForwardIt>
ForwardIt unique(ForwardIt first, ForwardIt last);
