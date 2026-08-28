// Сигнатура 1: Сума з нульовим початковим значенням типу елементів
template <class ExecutionPolicy, class ForwardIt>
typename std::iterator_traits<ForwardIt>::value_type
reduce(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last);

// Сигнатура 2: Сума з явним значенням init
template <class ExecutionPolicy, class ForwardIt, class T>
T reduce(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last, T init);

// Сигнатура 3: Редукція з користувацьким бінарним оператором
template <class ExecutionPolicy, class ForwardIt, class T, class BinaryOp>
T reduce(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last, T init, BinaryOp binary_op);
