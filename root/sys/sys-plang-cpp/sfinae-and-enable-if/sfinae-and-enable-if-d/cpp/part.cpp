// Перевантаження 1: для цілих чисел
template<typename T>
void serialize(Buffer& buf, T val) {
    buf.write_bytes(&val, sizeof(val));
}

// Перевантаження 2: для класів із власним методом
template<typename T>
void serialize(Buffer& buf, const T& obj) {
    obj.serialize(buf);
}
