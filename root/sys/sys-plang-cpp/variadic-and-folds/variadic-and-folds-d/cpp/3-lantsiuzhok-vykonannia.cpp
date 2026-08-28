template <typename... Callbacks>
void notify_observers(int event_id, Callbacks&&... callbacks) {
    // Згортка за комою викликає кожен callback послідовно
    (std::forward<Callbacks>(callbacks)(event_id), ...);
}

template <typename Target, typename... Values>
void push_all(Target& container, Values&&... vals) {
    (container.push_back(std::forward<Values>(vals)), ...);
}
