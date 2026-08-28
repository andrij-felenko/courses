// Унарна форма (Map -> Reduce): згортання результатів transform_op(x)
template <class ExecutionPolicy, class ForwardIt, class T, class BinaryOp, class UnaryOp>
T transform_reduce(ExecutionPolicy&& policy, 
                   ForwardIt first, ForwardIt last, 
                   T init, BinaryOp reduce_op, UnaryOp transform_op);

// Бінарна форма (Скалярний добуток): згортання результатів transform_op(x, y)
template <class ExecutionPolicy, class ForwardIt1, class ForwardIt2, class T, class BinaryOp1, class BinaryOp2>
T transform_reduce(ExecutionPolicy&& policy, 
                   ForwardIt1 first1, ForwardIt1 last1, 
                   ForwardIt2 first2, 
                   T init, BinaryOp1 reduce_op, BinaryOp2 transform_op);
