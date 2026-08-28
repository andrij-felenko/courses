// Подія виявлення нового унікального елемента RE-множини
typedef void (*OnElementFoundCb)(
    uint32_t task_id,
    int32_t element_value,
    uint64_t step_found,
    void *user_data
);

// Реєстрація обробника події виявлення елемента
EnumeratorStatus enumerator_set_element_callback(
    EnumeratorHandle *handle,
    OnElementFoundCb callback,
    void *user_data
);
