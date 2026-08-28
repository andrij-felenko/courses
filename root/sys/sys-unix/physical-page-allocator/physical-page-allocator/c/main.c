#include <linux/gfp.h>
#include <linux/mm.h>

/* Просимо 4 кадри (порядок 2) звичайної пам'яті */
struct page *pages = alloc_pages(GFP_KERNEL, 2);
if (!pages) {
    /* Немає суцільного блоку потрібного розміру */
    return -ENOMEM;
}

/* Отримуємо віртуальну адресу з прямого відображення */
void *buffer = page_address(pages);

/* Звільняємо ці 4 кадри назад системі приятелів */
__free_pages(pages, 2);
