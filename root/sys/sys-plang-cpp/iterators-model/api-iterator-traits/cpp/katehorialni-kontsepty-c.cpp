namespace std {
    // Ітератор вводу (читання однопрохідного потоку)
    template<typename I>
    concept input_iterator =
        std::input_or_output_iterator<I> &&
        std::indirectly_readable<I> &&
        requires(I i) {
            typename std::iter_concept_t<I>;
        };

    // Ітератор виводу (однопрохідний запис у потік або контейнер)
    template<typename I, typename T>
    concept output_iterator =
        std::input_or_output_iterator<I> &&
        std::indirectly_writable<I, T> &&
        requires(I i, T&& val) {
            *i++ = std::forward<T>(val);
        };

    // Однонапрямлений ітератор (багаторазовий прохід multi-pass)
    template<typename I>
    concept forward_iterator =
        std::input_iterator<I> &&
        std::derived_from<std::iter_concept_t<I>, std::forward_iterator_tag> &&
        std::incrementable<I> &&
        std::sentinel_for<I, I>;

    // Двонапрямлений ітератор (підтримка оператора декременту)
    template<typename I>
    concept bidirectional_iterator =
        std::forward_iterator<I> &&
        std::derived_from<std::iter_concept_t<I>, std::bidirectional_iterator_tag> &&
        requires(I i) {
            { --i } -> std::same_as<I&>;
            { i-- } -> std::same_as<I>;
        };

    // Ітератор довільного доступу (зсув та арифметичні оператори за O(1))
    template<typename I>
    concept random_access_iterator =
        std::bidirectional_iterator<I> &&
        std::derived_from<std::iter_concept_t<I>, std::random_access_iterator_tag> &&
        std::totally_ordered<I> &&
        std::sized_sentinel_for<I, I> &&
        requires(I i, const I j, const std::iter_difference_t<I> n) {
            { i += n } -> std::same_as<I&>;
            { i -= n } -> std::same_as<I&>;
            { j +  n } -> std::same_as<I>;
            { n +  j } -> std::same_as<I>;
            { j -  n } -> std::same_as<I>;
            { j[n]   } -> std::same_as<std::iter_reference_t<I>>;
        };

    // Ітератор суцільної пам'яті (гарантія розташування елементів у RAM)
    template<typename I>
    concept contiguous_iterator =
        std::random_access_iterator<I> &&
        std::derived_from<std::iter_concept_t<I>, std::contiguous_iterator_tag> &&
        std::is_lvalue_reference_v<std::iter_reference_t<I>> &&
        std::same_as<std::iter_value_t<I>, std::remove_cvref_t<std::iter_reference_t<I>>> &&
        requires(const I& i) {
            { std::to_address(i) } -> std::same_as<std::add_pointer_t<std::iter_reference_t<I>>>;
        };
}
