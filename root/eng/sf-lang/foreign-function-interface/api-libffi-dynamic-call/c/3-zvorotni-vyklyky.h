/* Виділення виконуваної пам'яті для трампліна */
void* ffi_closure_alloc(size_t size, void **code);

/* Налаштування прив'язки трампліна до обробника */
ffi_status ffi_prep_closure_loc(
    ffi_closure *closure,
    ffi_cif     *cif,
    void       (*fun)(ffi_cif *cif, void *ret, void **args, void *user_data),
    void        *user_data,
    void        *codeloc
);

/* Вивільнення пам'яті замикання */
void ffi_closure_free(void *closure);
