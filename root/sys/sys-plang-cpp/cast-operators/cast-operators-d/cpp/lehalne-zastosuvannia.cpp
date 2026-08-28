class TextBuffer {
public:
    const char& operator[](size_t idx) const noexcept {
        // Складна логіка перевірки меж, блокування м'ютекса, логування
        return data_[idx];
    }

    char& operator[](size_t idx) noexcept {
        // Викликаємо const-версію та знімаємо const з поверненого посилання
        return const_cast<char&>(
            static_cast<const TextBuffer&>(*this)[idx]
        );
    }

private:
    char data_[1024]{};
};
