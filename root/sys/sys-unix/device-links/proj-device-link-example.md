# Приклад створення зв'язку

Приклад C-коду в драйвері споживача, який встановлює залежність від постачальника — тут це IOMMU:

:::code proj-device-link-example/c/main.c

Керовані зв'язки не видаляють руками: за `Documentation/driver-api/device_link.rst` їх видаляє сам driver core відповідно до прапорців `DL_FLAG_AUTOREMOVE_CONSUMER` / `DL_FLAG_AUTOREMOVE_SUPPLIER`, а `device_link_del()` описаний у kernel-doc як видалення саме stateless-зв'язку. Виклик на керованому впирається в `device_link_put_kref()` у `drivers/base/core.c`: там `kref_put()` роблять лише для stateless-зв'язку, окремо мовчки видаляють зв'язок незареєстрованого споживача, а решта випадків — тобто наш — падає в `WARN(1, "Unable to drop a managed device link reference\n")`.

Просто дописати `DL_FLAG_STATELESS` до прапорців — не вихід одразу з двох причин. По-перше, його поєднання з `DL_FLAG_AUTOREMOVE_CONSUMER` (як і з `DL_FLAG_AUTOREMOVE_SUPPLIER` чи `DL_FLAG_AUTOPROBE_CONSUMER`) недійсне, і `device_link_add()` поверне `NULL` одразу. По-друге, stateless-зв'язок не дає того порядку `probe`/`unbind`, заради якого його тут і заводять, — лишається саме керування живленням.
