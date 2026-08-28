// Унарна трансформація: y[i] = op(x[i])
template <class ExecutionPolicy, class ForwardIt1, class ForwardIt2, class UnaryOperation>
ForwardIt2 transform(ExecutionPolicy&& policy, 
                     ForwardIt1 first1, ForwardIt1 last1, 
                     ForwardIt2 d_first, UnaryOperation unary_op);

// Бінарна трансформація: z[i] = op(x[i], y[i])
template <class ExecutionPolicy, class ForwardIt1, class ForwardIt2, class ForwardIt3, class BinaryOperation>
ForwardIt3 transform(ExecutionPolicy&& policy, 
                     ForwardIt1 first1, ForwardIt1 last1, 
                     ForwardIt2 first2, ForwardIt3 d_first, BinaryOperation binary_op);
