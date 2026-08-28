class AutoRegister {
public:
    AutoRegister(SubsystemNode& node) noexcept {
        g_registry.register_subsystem(&node);
    }
};

#define REGISTER_SUBSYSTEM(name_str, priority_num, init_func) \
    static SubsystemNode s_node_##init_func{name_str, priority_num, init_func}; \
    static AutoRegister s_autoreg_##init_func{s_node_##init_func}
