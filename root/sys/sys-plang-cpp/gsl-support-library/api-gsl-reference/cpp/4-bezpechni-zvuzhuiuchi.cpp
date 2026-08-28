namespace gsl {
    struct narrowing_error : public std::exception {
        const char* what() const noexcept override {
            return "gsl::narrowing_error: target type cannot hold source value";
        }
    };

    template <class Target, class Source>
    constexpr Target narrow(Source u);

    template <class Target, class Source>
    constexpr Target narrow_cast(Source&& u) noexcept;
}
