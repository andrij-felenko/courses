enum class ManagerOp {
    Destroy,
    Clone,
    Move,
    GetTargetType,
    GetTarget
};

template <typename F>
static void manager_func(void* dest, void* src, ManagerOp op) {
    switch (op) {
        case ManagerOp::Destroy:
            reinterpret_cast<F*>(dest)->~F();
            break;
        case ManagerOp::Clone:
            new (dest) F(*reinterpret_cast<const F*>(src));
            break;
        case ManagerOp::Move:
            new (dest) F(std::move(*reinterpret_cast<F*>(src)));
            reinterpret_cast<F*>(src)->~F();
            break;
        case ManagerOp::GetTargetType:
            *reinterpret_cast<const std::type_info**>(dest) = &typeid(F);
            break;
        case ManagerOp::GetTarget:
            *reinterpret_cast<void**>(dest) = dest;
            break;
    }
}
