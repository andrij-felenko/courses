asmlinkage __visible void *extract_kernel(void *rmode, unsigned char *heap,
                                  unsigned char *input_data,
                                  unsigned long input_len,
                                  unsigned long output,
                                  unsigned long output_len)
{
    /* 1. Налаштувати рання консоль друку (earlyprintk / serial) */
    sanitize_boot_params(rmode);
    
    /* 2. Знайти випадкове місце для KASLR */
    choose_random_location((unsigned long)input_data, input_len,
                           &output, output_len, &virt_addr);

    /* 3. Розпакувати стиснутий payload (piggy.o) у фізичну пам'ять */
    __decompress(input_data, input_len, NULL, NULL, output, output_len,
                 NULL, error);

    /* 4. Повернути фізичну адресу розпакованого коду vmlinux */
    return (void *)output;
}
