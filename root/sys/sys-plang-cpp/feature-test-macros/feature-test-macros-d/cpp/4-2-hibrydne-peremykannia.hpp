#pragma once

#include <type_traits>

#if defined(__cpp_concepts) && __cpp_concepts >= 201907L

    // Гілка сучасного C++20: декларативні концепції та швидка діагностика
    template <typename T>
    concept Serializable = requires(T a) {
        { a.serialize() } -> std::same_as<void>;
    };

    template <Serializable T>
    void process_message(const T& msg) {
        msg.serialize();
    }

#else

    // Гілка зворотної сумісності C++14: SFINAE через std::enable_if_t
    template <typename T, typename = void>
    struct is_serializable : std::false_type {};

    template <typename T>
    struct is_serializable<T, std::void_t<decltype(std::declval<T>().serialize())>> 
        : std::true_type {};

    template <typename T, typename = std::enable_if_t<is_serializable<T>::value>>
    void process_message(const T& msg) {
        msg.serialize();
    }

#endif
