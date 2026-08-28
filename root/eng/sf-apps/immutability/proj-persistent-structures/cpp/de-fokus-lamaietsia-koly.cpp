// Черга з двох незмінних списків. front — звідки беремо, back — куди кладемо.
template <typename T>
struct Queue {
    List<T> front;
    List<T> back;
};

template <typename T>
Queue<T> push(Queue<T> q, T v) {                 // додати — дешево, у back
    return { q.front, prepend(std::move(v), q.back) };
}
