// Пошук першого входження
template <class ExecutionPolicy, class ForwardIt, class T>
ForwardIt find(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last, const T& value);

// Пошук за предикатом
template <class ExecutionPolicy, class ForwardIt, class UnaryPredicate>
ForwardIt find_if(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last, UnaryPredicate p);

// Підрахунок елементів
template <class ExecutionPolicy, class ForwardIt, class UnaryPredicate>
typename std::iterator_traits<ForwardIt>::difference_type
count_if(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last, UnaryPredicate p);

// Перевірка умов
template <class ExecutionPolicy, class ForwardIt, class UnaryPredicate>
bool all_of(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last, UnaryPredicate p);

template <class ExecutionPolicy, class ForwardIt, class UnaryPredicate>
bool any_of(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last, UnaryPredicate p);
