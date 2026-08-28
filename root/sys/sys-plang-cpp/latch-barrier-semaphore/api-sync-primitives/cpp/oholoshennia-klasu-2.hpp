namespace std {
    template<class CompletionFunction = /* implementation-defined */>
    class barrier {
    public:
        using arrival_token = /* implementation-defined */;

        static constexpr ptrdiff_t max() noexcept;

        constexpr explicit barrier(ptrdiff_t expected,
                                   CompletionFunction f = CompletionFunction());
        ~barrier();

        barrier(const barrier&) = delete;
        barrier& operator=(const barrier&) = delete;

        [[nodiscard]] arrival_token arrive(ptrdiff_t update = 1);
        void wait(arrival_token&& arrival) const;
        void arrive_and_wait();
        void arrive_and_drop();

    private:
        /* implementation-defined стан (лічильники поточної та наступної фаз) */
    };
}
