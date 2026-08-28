// Замінити k-й елемент (рахуючи від голови, з 0). Мусимо перебудувати ВСЕ
// до k-го включно, бо кожен вузол перед зміненим тримає next, який тепер інший.
template <typename T>
List<T> setAt(List<T> lst, int k, T v) {
    if (!lst) return nullptr;                       // вихід за межі — тут просто край
    if (k == 0)
        return prepend(std::move(v), lst->next);    // новий вузол зі старим хвостом
    // інакше: новий вузол зі СТАРИМ значенням, але новим (перебудованим) хвостом
    return std::make_shared<Node<T>>(lst->value, setAt(lst->next, k - 1, std::move(v)));
}
