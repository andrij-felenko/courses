// registry.hpp
class Registry {
public:
    Registry(); // Динамічний конструктор
    void add_module(const char* name);
};
extern Registry g_registry;

// module_network.cpp
struct NetworkRegistrar {
    NetworkRegistrar() {
        g_registry.add_module("Network"); // Ризик SIOF!
    }
};
static NetworkRegistrar s_network_reg;
