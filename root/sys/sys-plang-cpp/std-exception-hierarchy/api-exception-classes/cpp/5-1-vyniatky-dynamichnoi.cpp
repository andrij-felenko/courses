namespace std {
    class bad_alloc : public exception {
    public:
        bad_alloc() noexcept;
        bad_alloc(const bad_alloc&) noexcept;
        bad_alloc& operator=(const bad_alloc&) noexcept;
        virtual const char* what() const noexcept override;
    };

    class bad_array_new_length : public bad_alloc {
    public:
        bad_array_new_length() noexcept;
        virtual const char* what() const noexcept override;
    };
}
