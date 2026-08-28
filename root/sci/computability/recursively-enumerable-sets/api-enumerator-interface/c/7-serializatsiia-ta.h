// Серіалізація поточного стану двигуна у файл
EnumeratorStatus enumerator_serialize_state(
    const EnumeratorHandle *handle,
    const char *file_path
);

// Відновлення стану двигуна з файлу контрольної точки
EnumeratorStatus enumerator_deserialize_state(
    const char *file_path,
    EnumeratorHandle **out_handle
);
