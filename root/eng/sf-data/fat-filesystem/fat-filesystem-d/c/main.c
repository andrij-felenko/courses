#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#pragma pack(push, 1)
typedef struct {
    uint8_t  BS_jmpBoot[3];
    char     BS_OEMName[8];
    uint16_t BPB_BytsPerSec;
    uint8_t  BPB_SecPerClus;
    uint16_t BPB_RsvdSecCnt;
    uint8_t  BPB_NumFATs;
    uint16_t BPB_RootEntCnt;
    uint16_t BPB_TotSec16;
    uint8_t  BPB_Media;
    uint16_t BPB_FATSz16;
    uint16_t BPB_SecPerTrk;
    uint16_t BPB_NumHeads;
    uint32_t BPB_HiddSec;
    uint32_t BPB_TotSec32;
    uint32_t BPB_FATSz32;
    uint16_t BPB_ExtFlags;
    uint16_t BPB_FSVer;
    uint32_t BPB_RootClus;
    uint16_t BPB_FSInfo;
    uint16_t BPB_BkBootSec;
    uint8_t  BPB_Reserved[12];
    uint8_t  BS_DrvNum;
    uint8_t  BS_Reserved1;
    uint8_t  BS_BootSig;
    uint32_t BS_VolID;
    char     BS_VolLab[11];
    char     BS_FilSysType[8];
    uint8_t  BS_BootCode[420];
    uint16_t BS_Signature;
} FAT32_BootRecord;
#pragma pack(pop)

/* Розрахунок LBA-сектора для кластера N */
uint32_t fat32_cluster_to_lba(const FAT32_BootRecord *bpb, uint32_t cluster) {
    uint32_t root_dir_sectors = ((bpb->BPB_RootEntCnt * 32) + (bpb->BPB_BytsPerSec - 1)) / bpb->BPB_BytsPerSec;
    uint32_t fat_sz = bpb->BPB_FATSz16 ? bpb->BPB_FATSz16 : bpb->BPB_FATSz32;
    uint32_t first_data_sec = bpb->BPB_RsvdSecCnt + (bpb->BPB_NumFATs * fat_sz) + root_dir_sectors;
    return first_data_sec + (cluster - 2) * bpb->BPB_SecPerClus;
}

/* Отримання номера наступного кластера з буфера FAT */
uint32_t fat32_get_next_cluster(const uint8_t *fat_table_sector, uint32_t cluster, uint16_t bytes_per_sec) {
    uint32_t fat_offset = cluster * 4;
    uint32_t ent_offset = fat_offset % bytes_per_sec;
    uint32_t entry = *(const uint32_t*)(fat_table_sector + ent_offset);
    return entry & 0x0FFFFFFF; /* Маскуємо 28 бітів */
}
