/* Структури статистики ядра Linux у C */
struct macsec_dev_stats {
    __u64 OutPktsUntagged;  /* Пакетів відправлено без SecTAG (коли encrypt off) */
    __u64 InPktsUntagged;   /* Вхідних кадрів без SecTAG при validate strict */
    __u64 InPktsBadTag;     /* Вхідних кадрів із пошкодженим/невалідним заголовком SecTAG */
    __u64 InPktsUnknownSCI; /* Вхідних кадрів із невідомим SCI (немає відповідного RX SC) */
    __u64 InPktsNoSCI;      /* Вхідних кадрів без SCI, коли SCI вимагається */
    __u64 InPktsOverrun;    /* Кадрів відкинуто через перевищення апаратних лімітів */
};

struct macsec_rx_sc_stats {
    __u64 InPktsOK;         /* Успішно дешифрованих та автентифікованих кадрів */
    __u64 InPktsUnchecked;  /* Кадрів пропущено в режимі validate disabled */
    __u64 InPktsDelayed;    /* Кадрів отримано із запізненням, але в межах вікна Replay Window */
    __u64 InPktsLate;       /* Кадрів відкинуто через старий PN (поза межами Replay Window) */
    __u64 InPktsInvalid;    /* Кадрів відкинуто через помилку підпису ICV */
    __u64 InPktsNotValid;   /* Кадрів із невалідним ICV у режимі validate check */
};
