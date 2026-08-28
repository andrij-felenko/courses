template <typename Derived>
class Readable {
public:
    void read() const {
        // Константне приведення для const-методів
        static_cast<const Derived*>(this)->read_impl();
    }

    void write() {
        // Неконстантне приведення для модифікуючих методів
        static_cast<Derived*>(this)->write_impl();
    }
};

class FileStream : public Readable<FileStream> {
public:
    void read_impl() const {
        // Читання даних без зміни стану
    }

    void write_impl() {
        // Модифікація стану файлу
    }
};
