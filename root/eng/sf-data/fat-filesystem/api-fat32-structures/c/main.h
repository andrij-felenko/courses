#ifndef FAT32_STRUCTS_H
#define FAT32_STRUCTS_H

#include <stdint.h>

#pragma pack(push, 1)

/* Базовий та розширений завантажувальний сектор FAT32 */
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

    /* FAT32 Extended Structure */
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
} FAT32_BootSector;

/* Структура сектора FSInfo */
typedef struct {
    uint32_t FSI_LeadSig;      /* 0x41615252 */
    uint8_t  FSI_Reserved1[480];
    uint32_t FSI_StrucSig;     /* 0x61417272 */
    uint32_t FSI_Free_Count;
    uint32_t FSI_Nxt_Free;
    uint8_t  FSI_Reserved2[12];
    uint32_t FSI_TrailSig;     /* 0xAA550000 */
} FAT32_FSInfo;

/* Запис короткого імені 8.3 (SFN) */
typedef struct {
    char     DIR_Name[8];
    char     DIR_Ext[3];
    uint8_t  DIR_Attr;
    uint8_t  DIR_NTRes;
    uint8_t  DIR_CrtTimeTenth;
    uint16_t DIR_CrtTime;
    uint16_t DIR_CrtDate;
    uint16_t DIR_LstAccDate;
    uint16_t DIR_FstClusHI;
    uint16_t DIR_WrtTime;
    uint16_t DIR_WrtDate;
    uint16_t DIR_FstClusLO;
    uint32_t DIR_FileSize;
} FAT_DirEntry;

/* Запис довгого імені файлу (LFN) */
typedef struct {
    uint8_t  LDIR_Ord;
    uint16_t LDIR_Name1[5];
    uint8_t  LDIR_Attr;        /* 0x0F */
    uint8_t  LDIR_Type;        /* 0x00 */
    uint8_t  LDIR_Chksum;
    uint16_t LDIR_Name2[6];
    uint16_t LDIR_FstClusLO;   /* 0x0000 */
    uint16_t LDIR_Name3[2];
} FAT_LFNEntry;

#pragma pack(pop)

#endif /* FAT32_STRUCTS_H */
