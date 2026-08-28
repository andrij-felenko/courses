#include <stdint.h>
#include <stdio.h>

// Заголовок ELF-ноти: так само влаштована будь-яка нота в .note-секції.
typedef struct {
    uint32_t namesz;   // довжина імені (для build-id це 4: "GNU\0")
    uint32_t descsz;   // довжина опису — самих байтів хешу (20 для SHA-1)
    uint32_t type;     // тип ноти; для build-id це NT_GNU_BUILD_ID == 3
    uint8_t  data[];   // спершу ім'я ("GNU\0"), одразу за ним — байти хешу
} elf_note_t;

// Символ на початок секції .note.gnu.build-id — його дає компонувальник.
extern const elf_note_t g_note_build_id;

// Надрукувати власний Build-ID тими самими 40 шістнадцятковими цифрами,
// що їх покаже readelf -n на хості. Саме цей рядок іде в лог.
void print_build_id(void) {
    // Байти хешу лежать одразу за ім'ям ("GNU\0"), тобто зі зсувом namesz.
    const uint8_t *id = &g_note_build_id.data[g_note_build_id.namesz];
    printf("Build ID: ");
    for (uint32_t i = 0; i < g_note_build_id.descsz; i++) {
        printf("%02x", id[i]);
    }
    printf("\n");
}
