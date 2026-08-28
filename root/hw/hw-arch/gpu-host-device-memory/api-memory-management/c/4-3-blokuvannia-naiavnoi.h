/* CUDA Runtime API: блокування наявного віртуального діапазону ОС */
cudaError_t cudaHostRegister(void *ptr, size_t size, unsigned int flags);
cudaError_t cudaHostUnregister(void *ptr);

/* Прапорці:
 * cudaHostRegisterDefault    - фіксація сторінок
 * cudaHostRegisterPortable   - доступність усім контекстам
 * cudaHostRegisterMapped     - відображення адрес у простір GPU
 * cudaHostRegisterIoMemory   - для пам'яті сторонніх PCIe пристроїв
 */
