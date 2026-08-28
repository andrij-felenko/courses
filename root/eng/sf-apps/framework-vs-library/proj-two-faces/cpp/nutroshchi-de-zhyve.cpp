private:
    struct Req {
        int               fd;
        std::string       payload;
        int               left;          // скільки спроб іще лишилось
        void*             tag;
        Clock::time_point sent_at;
        std::multimap<Clock::time_point, Id>::iterator timer;
    };

    void send_probe(Id id, Req& r, Clock::time_point now) noexcept;
    void finish(Id id, Req& r, Status st, int err,
                std::chrono::milliseconds rtt) noexcept;
    void touch_watches() noexcept { ++generation_; watches_dirty_ = true; }

    std::chrono::milliseconds rto_;
    int                       tries_;
    Id                        last_id_ = 0;
    std::unordered_map<Id, Req>          reqs_;
    std::unordered_map<int, Id>          by_fd_;
    std::multimap<Clock::time_point, Id> timers_;   // упорядкований за строком
    std::deque<Event>                    events_;
    mutable std::vector<Watch>           cache_;
    mutable bool                         watches_dirty_ = true;
    std::uint64_t                        generation_    = 0;
