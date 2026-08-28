// C++20 Концепти: чіткі, виразні та швидкі при компіляції
template<typename T>
concept has_draw = requires(T&& t) {
    std::forward<T>(t).draw();
};

template<has_draw T>
void draw_cpo_impl(T&& t) {
    std::forward<T>(t).draw();
}
