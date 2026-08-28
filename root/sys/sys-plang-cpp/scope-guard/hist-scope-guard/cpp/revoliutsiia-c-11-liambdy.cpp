template <typename F>
class CustomScopeGuard {
    F fn_;
    bool active_{true};
public:
    explicit CustomScopeGuard(F fn) : fn_(std::move(fn)) {}
    ~CustomScopeGuard() { if (active_) fn_(); }
    void dismiss() noexcept { active_ = false; }
    CustomScopeGuard(CustomScopeGuard&& o) noexcept 
        : fn_(std::move(o.fn_)), active_(std::exchange(o.active_, false)) {}
};
