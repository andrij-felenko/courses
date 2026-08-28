/* Чи оголосив гіпервізор паравіртуальне скидання TLB.
   Збірка: cc -O2 -o pvtlb pvtlb.c    Запуск: усередині гостя, прав не потрібно. */
#include <cpuid.h>
#include <stdio.h>
#include <string.h>

#define KVM_FEATURE_STEAL_TIME    5
#define KVM_FEATURE_PV_TLB_FLUSH  9
#define KVM_HINTS_REALTIME        0

int main(void)
{
    unsigned int eax, ebx, ecx, edx;
    char sig[13] = { 0 };

    /* Біт «виконуюся під гіпервізором» — листок 1, ECX біт 31. Без нього
       листків 0x4000_xxxx не існує, і прочитане з них буде сміттям. */
    __cpuid(1, eax, ebx, ecx, edx);
    if (!(ecx & (1u << 31))) {
        printf("гіпервізора немає — машина фізична\n");
        return 1;
    }

    /* 0x40000000 — корінь гіпервізорного простору листків: підпис і межа. */
    __cpuid(0x40000000, eax, ebx, ecx, edx);
    memcpy(sig + 0, &ebx, 4);
    memcpy(sig + 4, &ecx, 4);
    memcpy(sig + 8, &edx, 4);

    if (strcmp(sig, "KVMKVMKVM") != 0) {
        printf("не KVM (підпис «%s») — питання не має сенсу\n", sig);
        return 1;
    }
    if (eax < 0x40000001) {
        printf("гіпервізор не віддає листка можливостей\n");
        return 1;
    }

    __cpuid(0x40000001, eax, ebx, ecx, edx);
    printf("PV_TLB_FLUSH   : %s\n", (eax >> KVM_FEATURE_PV_TLB_FLUSH) & 1 ? "є" : "нема");
    printf("STEAL_TIME     : %s\n", (eax >> KVM_FEATURE_STEAL_TIME)   & 1 ? "є" : "нема");
    printf("HINTS_REALTIME : %s\n", (edx >> KVM_HINTS_REALTIME)       & 1
                                    ? "є — PV-скидання буде вимкнено" : "нема");
    return 0;
}
