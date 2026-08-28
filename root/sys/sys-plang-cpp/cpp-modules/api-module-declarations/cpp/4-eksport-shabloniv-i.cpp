export template <typename T>
concept Serializable = requires(T a) {
    { a.serialize() } -> std::same_as<std::string>;
};

export template <Serializable T>
class MessageQueue {
public:
    void push(T msg);
    T pop();
};
