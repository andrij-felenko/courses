// Первинний шаблон інспектора контейнерів
template<typename T>
struct ContainerInspector {
    static constexpr bool is_container = false;
};

// Часткова спеціалізація для будь-якого шаблону з одним типом-параметром (наприклад, std::vector<T>)
template<template<typename, typename...> class Container, typename Element, typename... Rest>
struct ContainerInspector<Container<Element, Rest...>> {
    static constexpr bool is_container = true;
    using value_type = Element;
};
