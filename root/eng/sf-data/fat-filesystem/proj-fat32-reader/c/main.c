#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

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
} FAT32_BS;

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
} FAT_Dir;

typedef struct {
    uint8_t  LDIR_Ord;
    uint16_t LDIR_Name1[5];
    uint8_t  LDIR_Attr;
    uint8_t  LDIR_Type;
    uint8_t  LDIR_Chksum;
    uint16_t LDIR_Name2[6];
    uint16_t LDIR_FstClusLO;
    uint16_t LDIR_Name3[2];
} FAT_LFN;
#pragma pack(pop)

typedef struct {
    FILE      *file;
    FAT32_BS   bs;
    uint32_t   fat_start_lba;
    uint32_t   data_start_lba;
    uint32_t   bytes_per_clus;
} FAT32_Context;

/* Розрахунок контрольної суми короткого імені 8.3 */
static uint8_t calc_sfn_checksum(const uint8_t *sfn_name) {
    uint8_t sum = 0;
    for (int i = 0; i < 11; i++) {
        sum = ((sum & 1) ? 0x80 : 0) + (sum >> 1) + sfn_name[i];
    }
    return sum;
}

/* Ініціалізація контексту FAT32 */
bool fat32_init(FAT32_Context *ctx, const char *image_path) {
    ctx->file = fopen(image_path, "rb");
    if (!ctx->file) return false;

    if (fread(&ctx->bs, sizeof(FAT32_BS), 1, ctx->file) != 1) {
        fclose(ctx->file);
        return false;
    }

    if (ctx->bs.BS_Signature != 0xAA55 || ctx->bs.BPB_BytsPerSec == 0) {
        fclose(ctx->file);
        return false;
    }

    ctx->fat_start_lba = ctx->bs.BPB_RsvdSecCnt;
    ctx->data_start_lba = ctx->bs.BPB_RsvdSecCnt + (ctx->bs.BPB_NumFATs * ctx->bs.BPB_FATSz32);
    ctx->bytes_per_clus = (uint32_t)ctx->bs.BPB_BytsPerSec * ctx->bs.BPB_SecPerClus;
    return true;
}

void fat32_close(FAT32_Context *ctx) {
    if (ctx->file) {
        fclose(ctx->file);
        ctx->file = NULL;
    }
}

/* Перетворення номера кластера у фізичний LBA сектор */
static uint32_t cluster_to_lba(const FAT32_Context *ctx, uint32_t cluster) {
    return ctx->data_start_lba + (cluster - 2) * ctx->bs.BPB_SecPerClus;
}

/* Зчитування наступного кластера з таблиці FAT */
static uint32_t fat32_next_cluster(FAT32_Context *ctx, uint32_t current_cluster) {
    uint32_t fat_offset = current_cluster * 4;
    uint32_t fat_sec = ctx->fat_start_lba + (fat_offset / ctx->bs.BPB_BytsPerSec);
    uint32_t ent_offset = fat_offset % ctx->bs.BPB_BytsPerSec;

    long byte_pos = (long)fat_sec * ctx->bs.BPB_BytsPerSec + ent_offset;
    if (fseek(ctx->file, byte_pos, SEEK_SET) != 0) return 0x0FFFFFFF;

    uint32_t next_entry = 0;
    if (fread(&next_entry, sizeof(uint32_t), 1, ctx->file) != 1) return 0x0FFFFFFF;

    return next_entry & 0x0FFFFFFF; /* Ігноруємо старші 4 зарезервовані біти */
}

/* Зчитування повного кластера даних у пам'ять */
bool fat32_read_cluster(FAT32_Context *ctx, uint32_t cluster, uint8_t *buffer) {
    uint32_t lba = cluster_to_lba(ctx, cluster);
    long byte_pos = (long)lba * ctx->bs.BPB_BytsPerSec;

    if (fseek(ctx->file, byte_pos, SEEK_SET) != 0) return false;
    return fread(buffer, ctx->bytes_per_clus, 1, ctx->file) == 1;
}

/* Виведення вмісту кореневого каталогу та зчитування цільового файлу */
void fat32_list_root(FAT32_Context *ctx) {
    uint8_t *clus_buf = (uint8_t*)malloc(ctx->bytes_per_clus);
    if (!clus_buf) return;

    uint32_t curr_clus = ctx->bs.BPB_RootClus;
    char lfn_buf[256] = {0};
    int lfn_chars = 0;
    uint8_t expected_chksum = 0;

    while (curr_clus < 0x0FFFFFF8 && curr_clus >= 2) {
        if (!fat32_read_cluster(ctx, curr_clus, clus_buf)) break;

        FAT_Dir *entries = (FAT_Dir*)clus_buf;
        size_t count = ctx->bytes_per_clus / sizeof(FAT_Dir);

        for (size_t i = 0; i < count; i++) {
            FAT_Dir *entry = &entries[i];

            if ((uint8_t)entry->DIR_Name[0] == 0x00) {
                /* Більше дійсних записів у каталозі немає */
                free(clus_buf);
                return;
            }
            if ((uint8_t)entry->DIR_Name[0] == 0xE5) {
                lfn_chars = 0;
                continue; /* Вилучений запис */
            }

            if (entry->DIR_Attr == 0x0F) {
                /* Запис VFAT LFN */
                FAT_LFN *lfn = (FAT_LFN*)entry;
                expected_chksum = lfn->LDIR_Chksum;

                /* Декодуємо 13 символів UTF-16LE в ASCII/UTF-8 */
                uint16_t chars16[13];
                memcpy(&chars16[0], lfn->LDIR_Name1, 10);
                memcpy(&chars16[5], lfn->LDIR_Name2, 12);
                memcpy(&chars16[11], lfn->LDIR_Name3, 4);

                int seq = (lfn->LDIR_Ord & 0x1F) - 1;
                for (int c = 0; c < 13; c++) {
                    if (chars16[c] == 0x0000 || chars16[c] == 0xFFFF) break;
                    if (seq * 13 + c < 255) {
                        lfn_buf[seq * 13 + c] = (char)(chars16[c] & 0xFF);
                        if (seq * 13 + c >= lfn_chars) lfn_chars = seq * 13 + c + 1;
                    }
                }
                continue;
            }

            /* Стандартний запис SFN 8.3 */
            if (entry->DIR_Attr & 0x08) {
                lfn_chars = 0;
                continue; /* Пропускаємо мітку тома */
            }

            lfn_buf[lfn_chars] = '\0';
            uint8_t actual_chksum = calc_sfn_checksum((uint8_t*)entry->DIR_Name);
            const char *display_name = (lfn_chars > 0 && expected_chksum == actual_chksum) ? lfn_buf : entry->DIR_Name;

            uint32_t first_clus = ((uint32_t)entry->DIR_FstClusHI << 16) | entry->DIR_FstClusLO;
            bool is_dir = (entry->DIR_Attr & 0x10) != 0;

            printf("[%s] %-24s | Кластер: %-6u | Розмір: %u байтів\n",
                   is_dir ? "DIR " : "FILE", display_name, first_clus, entry->DIR_FileSize);

            lfn_chars = 0;
        }

        curr_clus = fat32_next_cluster(ctx, curr_clus);
    }

    free(clus_buf);
}
