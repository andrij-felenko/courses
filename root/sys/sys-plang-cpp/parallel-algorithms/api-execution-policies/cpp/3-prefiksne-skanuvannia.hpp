// std::inclusive_scan: y[i] = x[0] + ... + x[i]
template <class ExecutionPolicy, class ForwardIt1, class ForwardIt2>
ForwardIt2 inclusive_scan(ExecutionPolicy&& policy, 
                          ForwardIt1 first, ForwardIt1 last, 
                          ForwardIt2 d_first);

template <class ExecutionPolicy, class ForwardIt1, class ForwardIt2, class BinaryOp, class T>
ForwardIt2 inclusive_scan(ExecutionPolicy&& policy, 
                          ForwardIt1 first, ForwardIt1 last, 
                          ForwardIt2 d_first, BinaryOp binary_op, T init);

// std::exclusive_scan: y[0] = init, y[i] = init + x[0] + ... + x[i-1]
template <class ExecutionPolicy, class ForwardIt1, class ForwardIt2, class T>
ForwardIt2 exclusive_scan(ExecutionPolicy&& policy, 
                          ForwardIt1 first, ForwardIt1 last, 
                          ForwardIt2 d_first, T init);

template <class ExecutionPolicy, class ForwardIt1, class ForwardIt2, class T, class BinaryOp>
ForwardIt2 exclusive_scan(ExecutionPolicy&& policy, 
                          ForwardIt1 first, ForwardIt1 last, 
                          ForwardIt2 d_first, T init, BinaryOp binary_op);
