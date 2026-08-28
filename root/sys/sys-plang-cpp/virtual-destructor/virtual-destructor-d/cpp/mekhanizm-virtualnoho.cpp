// Псевдокод еквіваленту машинних інструкцій
if (handler != nullptr) {
    // 1. Отримати адресу vtable за зміщенням vptr усередині об'єкта
    void** vtable = *reinterpret_cast<void***>(handler);
    // 2. Отримати адресу слота Deleting Destructor (D0)
    using DeletingDtorFn = void(*)(void*);
    DeletingDtorFn dtor = reinterpret_cast<DeletingDtorFn>(vtable[SLOT_D0_DELETING_DTOR]);
    // 3. Непрямий виклик через покажчик на функцію
    dtor(handler);
}
