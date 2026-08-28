/* include/uapi/linux/virtio_balloon.h */
struct virtio_balloon_config {
    /* Кількість 4 КіБ сторінок, яку гіпервізор вимагає утримувати в балоні */
    __virtio32 num_pages;

    /* Фактична кількість 4 КіБ сторінок, захоплених драйвером гостя на цей момент */
    __virtio32 actual;

    /* Ідентифікатор команди для узгодження Free Page Hinting або значення отруєння */
    union {
        __virtio32 free_page_hint_cmd_id;
        __virtio32 poison_val;
    };

    /* Запасне поле розширення для майбутніх стандартів */
    __virtio32 free_page_hint_cmd_id_padding;
};
