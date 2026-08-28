class NonTemplateStorage {
protected:
    void raw_write(const void* data, size_t size) {
        // Звичайний нешаблонний код, що існує в бінарнику в єдиному примірнику
    }
};

template <typename Derived>
class DataWriter : private NonTemplateStorage {
public:
    void write_object() {
        Derived& self = *static_cast<Derived*>(this);
        this->raw_write(&self, sizeof(Derived));
    }
};
