union grant_entry_v2 {
    struct {
        uint16_t flags;
        domid_t  domid;
        uint32_t pad0;
        uint64_t frame;     /* 64-бітний MFN для систем з ОЗП понад 16 ТіБ */
    } full_page;
    struct {
        uint16_t flags;
        domid_t  domid;
        uint16_t page_off;  /* Зміщення всередині сторінки в байтах від початку кадру */
        uint16_t length;    /* Довжина дозволеного фрагмента в байтах */
        uint64_t frame;     /* MFN сторінки, фрагмент якої відкрито */
    } sub_page;
};
typedef union grant_entry_v2 grant_entry_v2_t;
