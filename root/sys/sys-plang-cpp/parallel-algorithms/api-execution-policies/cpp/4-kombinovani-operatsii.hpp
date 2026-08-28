// Трансформація + інклюзивне сканування
template <class ExecutionPolicy, class ForwardIt1, class ForwardIt2, class BinaryOp, class UnaryOp>
ForwardIt2 transform_inclusive_scan(ExecutionPolicy&& policy, 
                                    ForwardIt1 first, ForwardIt1 last, 
                                    ForwardIt2 d_first, 
                                    BinaryOp binary_op, UnaryOp unary_op);

// Трансформація + ексклюзивне сканування
template <class ExecutionPolicy, class ForwardIt1, class ForwardIt2, class T, class BinaryOp, class UnaryOp>
ForwardIt2 transform_exclusive_scan(ExecutionPolicy&& policy, 
                                    ForwardIt1 first, ForwardIt1 last, 
                                    ForwardIt2 d_first, 
                                    T init, BinaryOp binary_op, UnaryOp unary_op);
