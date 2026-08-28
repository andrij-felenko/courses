#include <stdio.h>
#include <stdint.h>
#include <stddef.h>

/* Моделювання структури повної таблиці Itanium ABI з метаданими */
typedef struct {
    ptrdiff_t vbase_offset;   /* Зсув до віртуальної бази: слот [-3] */
    ptrdiff_t offset_to_top;  /* Зсув до початку повного об'єкта: слот [-2] */
    void*     rtti_info;      /* Покажчик на RTTI: слот [-1] */
    void (*vfunc)(void*);     /* Точка входу: слот [0] */
} CompleteVTable;

typedef struct {
    int v_data;
} VirtualBaseData;

typedef struct {
    const void* vptr;         /* Вказує на поле vfunc у CompleteVTable */
    int d_data;
    VirtualBaseData vbase;    /* Спільна віртуальна база в кінці об'єкта */
} ManualDiamond;

static void manual_vfunc(void* self) {
    (void)self;
    printf("ManualDiamond::vfunc виконано\n");
}

static const CompleteVTable g_full_vtable = {
    .vbase_offset  = offsetof(ManualDiamond, vbase),
    .offset_to_top = 0,
    .rtti_info     = NULL,
    .vfunc         = manual_vfunc
};

int main(void) {
    ManualDiamond obj;
    obj.vptr = &g_full_vtable.vfunc; /* Точка входу vtable відповідає слоту [0] */
    obj.d_data = 888;
    obj.vbase.v_data = 777;

    /* Зчитування від'ємного зсуву з таблиці */
    const void** vtable_entry = (const void**)obj.vptr;
    ptrdiff_t vbase_offset = (ptrdiff_t)vtable_entry[-3];

    printf("=== Ручне читання зсувів віртуальної бази в C ===\n");
    printf("Зсув до віртуальної бази з vtable[-3]: %td байтів\n", vbase_offset);

    VirtualBaseData* vbase_ptr = (VirtualBaseData*)((char*)&obj + vbase_offset);
    printf("Значення vbase_ptr->v_data: %d\n", vbase_ptr->v_data);

    return 0;
}
