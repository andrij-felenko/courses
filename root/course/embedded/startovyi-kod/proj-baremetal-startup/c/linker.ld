/* linker.ld — карта розміщення секцій.
   Ціль: ARM Cortex-M4F, 512 КБ Flash, 128 КБ SRAM (STM32F405/407 і рідня).
   Той самий скрипт лінкує і приклад мовою C, і приклад мовою C++:
   змінюючи чип, правлять лише блок MEMORY. */

ENTRY(Reset_Handler)

MEMORY
{
  FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 512K
  RAM   (rwx) : ORIGIN = 0x20000000, LENGTH = 128K
}

/* Вершина головного стека — самий кінець RAM. Адреса кратна 8 байтам,
   бо AAPCS вимагає вирівняного на подвійне слово SP на межі виклику. */
_estack = ORIGIN(RAM) + LENGTH(RAM);

_Min_Heap_Size  = 0x200;   /* мінімальний резерв під купу — 512 байтів  */
_Min_Stack_Size = 0x400;   /* гарантований резерв під стек — 1024 байти */

SECTIONS
{
  /* 1. Векторна таблиця лежить на початку Flash: перші два слова ядро читає
        апаратно, ще не виконавши жодної інструкції. Вирівнювання 512 байтів —
        вимога регістра SCB->VTOR: його молодші біти апаратно нульові, тож
        невирівняна таблиця «переїхала» б після релокації. */
  .isr_vector :
  {
    . = ALIGN(512);
    KEEP(*(.isr_vector))
    . = ALIGN(4);
  } >FLASH

  /* 2. Код і константи */
  .text :
  {
    . = ALIGN(4);
    *(.text)
    *(.text*)
    *(.rodata)
    *(.rodata*)
    *(.glue_7)             /* перехідники ARM↔Thumb від старих бібліотек */
    *(.glue_7t)
    KEEP(*(.init))
    KEEP(*(.fini))
    . = ALIGN(4);
    _etext = .;
  } >FLASH

  /* 2a. Таблиці розкрутки стека. Збірка йде з -fno-exceptions, тож вони майже
         порожні, але символи __exidx_start/__exidx_end потрібні самій libgcc. */
  .ARM.extab : { *(.ARM.extab* .gnu.linkonce.armextab.*) } >FLASH
  .ARM :
  {
    __exidx_start = .;
    *(.ARM.exidx*)
    __exidx_end = .;
  } >FLASH

  /* 3. Таблиці ініціалізаторів: .preinit_array виконується першим, далі
        .init_array — конструктори глобальних об'єктів C++ і функції з
        атрибутом __attribute__((constructor)). */
  .preinit_array :
  {
    . = ALIGN(4);
    PROVIDE_HIDDEN (__preinit_array_start = .);
    KEEP (*(.preinit_array*))
    PROVIDE_HIDDEN (__preinit_array_end = .);
    . = ALIGN(4);
  } >FLASH

  .init_array :
  {
    . = ALIGN(4);
    PROVIDE_HIDDEN (__init_array_start = .);
    KEEP (*(SORT(.init_array.*)))
    KEEP (*(.init_array*))
    PROVIDE_HIDDEN (__init_array_end = .);
    . = ALIGN(4);
  } >FLASH

  /* Деструктори глобальних об'єктів. На голому залізі програма не
     завершується, тож таблиця не виконується ніколи, — але лінкер мусить
     знати, куди її покласти, інакше зависне символ __dso_handle. */
  .fini_array :
  {
    . = ALIGN(4);
    PROVIDE_HIDDEN (__fini_array_start = .);
    KEEP (*(SORT(.fini_array.*)))
    KEEP (*(.fini_array*))
    PROVIDE_HIDDEN (__fini_array_end = .);
    . = ALIGN(4);
  } >FLASH

  /* Завантажувальна адреса (LMA) початкових значень .data у Flash. */
  _sidata = LOADADDR(.data);

  /* 4. Ініціалізовані змінні: живуть у RAM (VMA), лежать у Flash (LMA). */
  .data :
  {
    . = ALIGN(4);
    _sdata = .;
    *(.data)
    *(.data*)
    . = ALIGN(4);
    _edata = .;
  } >RAM AT> FLASH

  /* 5. Неініціалізовані змінні: у прошивці займають 0 байтів, тож занулити
        їх — обов'язок стартового коду. */
  .bss :
  {
    . = ALIGN(4);
    _sbss = .;
    __bss_start__ = _sbss;
    *(.bss)
    *(.bss*)
    *(COMMON)
    . = ALIGN(4);
    _ebss = .;
    __bss_end__ = _ebss;
  } >RAM

  /* 6. Перший вільний байт за глобальними змінними — початок купи для _sbrk.
        Резерв під купу і стек тут же перевіряється на етапі збирання: якщо
        глобальних змінних забагато, лінкер скаже «region RAM overflowed»,
        а не прошивка мовчки впаде на першому глибокому виклику. */
  ._user_heap_stack :
  {
    . = ALIGN(8);
    PROVIDE ( end  = . );
    PROVIDE ( _end = . );
    . = . + _Min_Heap_Size;
    . = . + _Min_Stack_Size;
    . = ALIGN(8);
  } >RAM

  /* Службовий опис архітектури; в образ прошивки не потрапляє. */
  .ARM.attributes 0 : { *(.ARM.attributes) }

  /DISCARD/ :
  {
    *(.comment)
    *(.note*)
  }
}

ASSERT((_estack & 7) == 0, "ПОМИЛКА: вершина стека _estack не вирівняна на 8 байтів")
ASSERT(ADDR(.isr_vector) == ORIGIN(FLASH), "ПОМИЛКА: .isr_vector не на початку Flash")
