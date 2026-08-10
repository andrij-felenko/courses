# Приклад створення зв'язку

Приклад C-коду в драйвері споживача, який встановлює залежність від постачальника — тут це IOMMU:

```c
#include <linux/device.h>
#include <linux/platform_device.h>

struct my_gpu_data {
    // ...
};

static int my_gpu_probe(struct platform_device *pdev)
{
    struct device *dev = &pdev->dev;
    struct my_gpu_data *gpu;
    struct device *iommu_dev;
    struct device_link *link;

    gpu = devm_kzalloc(dev, sizeof(*gpu), GFP_KERNEL);
    if (!gpu)
        return -ENOMEM;

    // Припустимо, ми знайшли struct device постачальника (IOMMU)
    iommu_dev = get_iommu_device_for_gpu(dev);
    if (!iommu_dev)
        return -EPROBE_DEFER;

    // Створюємо зв'язок: GPU (споживач) залежить від IOMMU (постачальник).
    // DL_FLAG_STATELESS не заданий, тож device_link_add() сам додасть
    // DL_FLAG_MANAGED: зв'язок керований. Він впливає на Runtime PM, і якщо
    // IOMMU вивантажать, GPU буде відв'язано автоматично перед ним.
    link = device_link_add(dev, iommu_dev,
                           DL_FLAG_PM_RUNTIME | DL_FLAG_AUTOREMOVE_CONSUMER);

    if (!link) {
        dev_err(dev, "Failed to create device link to IOMMU\n");
        return -EINVAL;
    }

    // Вказівник на керований зв'язок навмисно не зберігаємо: driver core
    // прибере зв'язок сам, і збережений вказівник вказував би вже в нікуди.
    platform_set_drvdata(pdev, gpu);
    return 0;
}

static void my_gpu_remove(struct platform_device *pdev)
{
    // Тут зі зв'язком робити нічого не треба: за DL_FLAG_AUTOREMOVE_CONSUMER
    // його прибере driver core, коли споживач відв'яжеться.
    // Викликати device_link_del() на керованому зв'язку НЕ можна.
}
```

Керовані зв'язки не видаляють руками: за `Documentation/driver-api/device_link.rst` їх видаляє сам driver core відповідно до прапорців `DL_FLAG_AUTOREMOVE_CONSUMER` / `DL_FLAG_AUTOREMOVE_SUPPLIER`, а `device_link_del()` описаний у kernel-doc як видалення саме stateless-зв'язку. Виклик на керованому впирається в `device_link_put_kref()` у `drivers/base/core.c`: там `kref_put()` роблять лише для stateless-зв'язку, окремо мовчки видаляють зв'язок незареєстрованого споживача, а решта випадків — тобто наш — падає в `WARN(1, "Unable to drop a managed device link reference\n")`.

Просто дописати `DL_FLAG_STATELESS` до прапорців — не вихід одразу з двох причин. По-перше, його поєднання з `DL_FLAG_AUTOREMOVE_CONSUMER` (як і з `DL_FLAG_AUTOREMOVE_SUPPLIER` чи `DL_FLAG_AUTOPROBE_CONSUMER`) недійсне, і `device_link_add()` поверне `NULL` одразу. По-друге, stateless-зв'язок не дає того порядку `probe`/`unbind`, заради якого його тут і заводять, — лишається саме керування живленням.
