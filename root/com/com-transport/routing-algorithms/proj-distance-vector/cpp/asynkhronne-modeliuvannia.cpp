struct MessageEvent {
    double timestamp;
    int sender_id;
    int receiver_id;
    std::vector<int> distance_vector;

    bool operator>(const MessageEvent& other) const {
        return timestamp > other.timestamp; // Мережевий час затримки
    }
};

std::priority_queue<MessageEvent, std::vector<MessageEvent>, std::greater<>> event_queue;
