// ХИБНА оболонка: свій обробник на кожен запит.
template <class OnEvent>
class Runner {
    probe::Core&                           core_;
    std::unordered_map<probe::Id, OnEvent> handlers_;   // ← знання про СПРАВУ
    std::unordered_map<probe::Id, std::string> names_;  // ← і ще одне
public:
    void probe_host(const std::string& name, sockaddr_in to, OnEvent h) {
        const auto id = core_.add(probe::Clock::now(), to, "ping");
        handlers_.emplace(id, std::move(h));            // ядро про це не знає
        names_.emplace(id, name);                       // і про це теж
    }
};
