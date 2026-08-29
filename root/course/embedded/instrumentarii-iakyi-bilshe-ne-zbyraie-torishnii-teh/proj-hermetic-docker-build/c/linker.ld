/* Розкладка образу. Головне тут — секція .meta одразу за таблицею векторів:
   її зсув наперед відомий, тож бутлоадер читає метадані з фіксованого місця,
   не розбираючи ELF. Символи __image_start/__image_end дають межі того, що
   реально їде у firmware.bin, — саме над цим діапазоном рахується CRC32. */

ENTRY(Reset_Handler)

MEMORY
{
    FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 512K
    RAM   (rwx) : ORIGIN = 0x20000000, LENGTH = 96K
}

_estack = ORIGIN(RAM) + LENGTH(RAM);

SECTIONS
{
    .vectors : ALIGN(4)
    {
        KEEP(*(.vectors))
        . = ALIGN(4);
    } > FLASH

    .meta : ALIGN(4)
    {
        __meta_start = .;
        KEEP(*(.meta))
        __meta_end = .;
        . = ALIGN(4);
    } > FLASH

    .text : ALIGN(4)
    {
        *(.text .text.*)
        *(.rodata .rodata.*)
        . = ALIGN(4);
    } > FLASH

    .data : ALIGN(4)
    {
        __data_start = .;
        *(.data .data.*)
        . = ALIGN(4);
        __data_end = .;
    } > RAM AT > FLASH

    __data_load = LOADADDR(.data);

    .bss (NOLOAD) : ALIGN(4)
    {
        __bss_start = .;
        *(.bss .bss.*)
        *(COMMON)
        . = ALIGN(4);
        __bss_end = .;
    } > RAM

    /* Діагностична скринька переживає теплий перезапуск: стартовий код її
       не чистить, тому вона й винесена з .bss. */
    .noinit (NOLOAD) : ALIGN(4)
    {
        *(.noinit .noinit.*)
        . = ALIGN(4);
    } > RAM

    /* Межі двійкового образу: від початку FLASH до кінця LMA секції .data —
       рівно стільки байтів віддає objcopy -O binary. */
    __image_start = ORIGIN(FLASH);
    __image_end   = LOADADDR(.data) + SIZEOF(.data);

    /DISCARD/ :
    {
        *(.comment)
        *(.ARM.attributes)
    }
}
