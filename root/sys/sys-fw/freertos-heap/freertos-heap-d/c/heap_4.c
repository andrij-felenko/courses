#include "freertos/FreeRTOS.h"

/* Внутрішній фрагмент алгоритму злиття heap_4.c */
static void prvInsertBlockIntoFreeList( BlockLink_t *pxBlockToInsert )
{
    BlockLink_t *pxIterator;
    uint8_t *puc;

    /* 1. Пошук позиції вставки за адресою: шукаємо блок, адреса якого менша за pxBlockToInsert */
    for( pxIterator = &xStart; pxIterator->pxNextFreeBlock < pxBlockToInsert; pxIterator = pxIterator->pxNextFreeBlock )
    {
        /* Простий прохід списком вперед */
    }

    /* 2. Перевірка злиття з ЛІВИМ сусідом (той, що попереду у списку) */
    puc = ( uint8_t * ) pxIterator;
    if( ( puc + pxIterator->xBlockSize ) == ( uint8_t * ) pxBlockToInsert )
    {
        /* Лівий сусід впритул прилягає до нашого блока: поглинаємо наш блок */
        pxIterator->xBlockSize += pxBlockToInsert->xBlockSize;
        pxBlockToInsert = pxIterator;
    }
    else
    {
        /* Якщо лівий сусід не прилягає, зв'язуємо вказівники */
        pxIterator->pxNextFreeBlock = pxBlockToInsert;
    }

    /* 3. Перевірка злиття з ПРАВИМ сусідом (наступний за адресою) */
    puc = ( uint8_t * ) pxBlockToInsert;
    if( ( puc + pxBlockToInsert->xBlockSize ) == ( uint8_t * ) pxIterator->pxNextFreeBlock )
    {
        if( pxIterator->pxNextFreeBlock != pxEnd )
        {
            /* Правий сусід прилягає до кінця нашого блока: поглинаємо правого сусіда */
            pxBlockToInsert->xBlockSize += pxIterator->pxNextFreeBlock->xBlockSize;
            pxBlockToInsert->pxNextFreeBlock = pxIterator->pxNextFreeBlock->pxNextFreeBlock;
        }
    }
    else
    {
        pxBlockToInsert->pxNextFreeBlock = pxIterator->pxNextFreeBlock;
    }
}
