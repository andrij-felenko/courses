from _sensor_backend import ffi, lib

def create_managed_context():
    # Нативна функція C виділяє пам'ять через malloc()
    raw_ctx = lib.sensor_context_create()
    if raw_ctx == ffi.NULL:
        raise MemoryError("Не вдалося ініціалізувати нативний контекст")

    # Прив'язуємо C-деструктор до об'єкта cdata
    # Коли gc_ctx збирається GC Python, автоматично викликається sensor_context_destroy(raw_ctx)
    gc_ctx = ffi.gc(raw_ctx, lib.sensor_context_destroy)
    return gc_ctx
