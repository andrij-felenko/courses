// Класичне послідовне накопичення (C++98)
template <class InputIt, class T>
T accumulate(InputIt first, InputIt last, T init);

template <class InputIt, class T, class BinaryOperation>
T accumulate(InputIt first, InputIt last, T init, BinaryOperation op);

// Паралельна згортка (C++17)
template <class ExecutionPolicy, class ForwardIt, class T, class BinaryOperation>
T reduce(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last, T init, BinaryOperation op);

// Трансформація та згортка (MapReduce)
template <class ExecutionPolicy, class ForwardIt1, class ForwardIt2, class T,
          class BinaryOp1, class BinaryOp2>
T transform_reduce(ExecutionPolicy&& policy, ForwardIt1 first1, ForwardIt1 last1,
                 ForwardIt2 first2, T init, BinaryOp1 transform_op, BinaryOp2 reduce_op);

// Генерація послідовності інкрементованих значень (v[0]=val, v[1]=val+1...)
template <class ForwardIt, class T>
void iota(ForwardIt first, ForwardIt last, T value);
