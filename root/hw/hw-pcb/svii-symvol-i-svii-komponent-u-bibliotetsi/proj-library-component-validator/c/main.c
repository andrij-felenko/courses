#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <ctype.h>

#define MAX_STR_LEN 128
#define MAX_ITEMS 512

typedef enum {
    PIN_TYPE_INPUT,
    PIN_TYPE_OUTPUT,
    PIN_TYPE_BIDIRECTIONAL,
    PIN_TYPE_TRISTATE,
    PIN_TYPE_PASSIVE,
    PIN_TYPE_POWER_IN,
    PIN_TYPE_POWER_OUT,
    PIN_TYPE_OPEN_DRAIN,
    PIN_TYPE_NOT_CONNECTED
} PinType;

const char* pin_type_to_string(PinType t) {
    switch (t) {
        case PIN_TYPE_INPUT:         return "Input";
        case PIN_TYPE_OUTPUT:        return "Output";
        case PIN_TYPE_BIDIRECTIONAL: return "Bidirectional";
        case PIN_TYPE_TRISTATE:      return "Tri-state";
        case PIN_TYPE_PASSIVE:       return "Passive";
        case PIN_TYPE_POWER_IN:      return "Power In";
        case PIN_TYPE_POWER_OUT:     return "Power Out";
        case PIN_TYPE_OPEN_DRAIN:    return "Open Drain";
        case PIN_TYPE_NOT_CONNECTED: return "Not Connected";
        default:                     return "Unknown";
    }
}

typedef struct {
    char number[32];
    char name[MAX_STR_LEN];
    char unit[8];
    PinType type;
    bool is_active_low;
} SymbolPin;

typedef struct {
    char number[32];
    char name[MAX_STR_LEN];
    bool is_mechanical;
} FootprintPad;

typedef struct {
    char symbol_pin_num[32];
    char footprint_pad_num[32];
} PinMapping;

typedef struct {
    char mpn[MAX_STR_LEN];
    char manufacturer[MAX_STR_LEN];
    char footprint_ref[MAX_STR_LEN];
    char datasheet_url[MAX_STR_LEN];
    
    SymbolPin pins[MAX_ITEMS];
    size_t pin_count;
    
    FootprintPad pads[MAX_ITEMS];
    size_t pad_count;
    
    PinMapping mappings[MAX_ITEMS];
    size_t mapping_count;
} ComponentDefinition;

// Перевірка буквено-цифрових позначень BGA за стандартом JEDEC
bool check_jedec_bga_rules(const char* pad_num, char* err_buf, size_t buf_len) {
    const char* forbidden = "IOQSXZ";
    for (size_t i = 0; i < strlen(pad_num); ++i) {
        char c = (char)toupper((unsigned char)pad_num[i]);
        if (strchr(forbidden, c) != NULL && isalpha((unsigned char)c)) {
            snprintf(err_buf, buf_len,
                     "Площадка BGA '%s' містить неприпустиму стандартом JEDEC літеру '%c'",
                     pad_num, c);
            return false;
        }
    }
    return true;
}

// Повний аудит бібліотечного компонента
int run_component_audit(const ComponentDefinition* comp) {
    int error_count = 0;
    int warning_count = 0;
    char error_buffer[256];

    printf("=====================================================\n");
    printf("АУДИТ КОМПОНЕНТА: %s (%s)\n", comp->mpn, comp->manufacturer);
    printf("Посадкове місце: %s\n", comp->footprint_ref);
    printf("=====================================================\n");

    // 1. Аудит атрибутів закупівлі BOM
    if (strlen(comp->mpn) == 0) {
        printf("[ПОМИЛКА] Відсутній номер деталі виробника (MPN)!\n");
        error_count++;
    }
    if (strlen(comp->manufacturer) == 0) {
        printf("[ПОМИЛКА] Відсутня назва фірми-виробника!\n");
        error_count++;
    }
    if (strlen(comp->footprint_ref) == 0) {
        printf("[ПОМИЛКА] Відсутня прив'язка посадкового місця!\n");
        error_count++;
    }
    if (strlen(comp->datasheet_url) == 0 || strncmp(comp->datasheet_url, "http", 4) != 0) {
        printf("[ПОПЕРЕДЖЕННЯ] Посилання на Datasheet порожнє або не є HTTP URL!\n");
        warning_count++;
    }

    // 2. Аудит виводів символу
    if (comp->pin_count == 0) {
        printf("[ПОМИЛКА] Символ не містить жодного виводу!\n");
        error_count++;
    }

    for (size_t i = 0; i < comp->pin_count; ++i) {
        const SymbolPin* p1 = &comp->pins[i];
        
        // Перевірка дублювання виводів у секції
        for (size_t j = i + 1; j < comp->pin_count; ++j) {
            const SymbolPin* p2 = &comp->pins[j];
            if (strcmp(p1->number, p2->number) == 0 && strcmp(p1->unit, p2->unit) == 0) {
                printf("[ПОМИЛКА] Дублювання виводу '%s' у секції Unit %s!\n",
                       p1->number, p1->unit);
                error_count++;
            }
        }

        // Перевірка синтаксису інверсії сигналів
        if (p1->is_active_low) {
            bool has_prefix = (p1->name[0] == '~' || p1->name[0] == 'n' || p1->name[0] == '/');
            bool has_suffix = (p1->name[strlen(p1->name) - 1] == '#' || 
                               (strlen(p1->name) >= 2 && strcmp(&p1->name[strlen(p1->name) - 2], "_N") == 0));
            if (!has_prefix && !has_suffix) {
                printf("[ПОПЕРЕДЖЕННЯ] Пін %s (%s) позначений як Active-Low, але не має позначки інверсії (~, n, #)!\n",
                       p1->number, p1->name);
                warning_count++;
            }
        }
    }

    // 3. Аудит площадок посадкового місця
    if (comp->pad_count == 0) {
        printf("[ПОМИЛКА] Посадкове місце не містить контактних площадок!\n");
        error_count++;
    }

    for (size_t i = 0; i < comp->pad_count; ++i) {
        const FootprintPad* pad1 = &comp->pads[i];
        
        // JEDEC BGA перевірка
        if (!check_jedec_bga_rules(pad1->number, error_buffer, sizeof(error_buffer))) {
            printf("[ПОМИЛКА] %s\n", error_buffer);
            error_count++;
        }

        // Перевірка дублювання номерів площадок
        for (size_t j = i + 1; j < comp->pad_count; ++j) {
            const FootprintPad* pad2 = &comp->pads[j];
            if (strcmp(pad1->number, pad2->number) == 0) {
                printf("[ПОМИЛКА] Посадкове місце містить дубльовану площадку номер '%s'!\n",
                       pad1->number);
                error_count++;
            }
        }
    }

    // 4. Аудит бієкції Pin-to-Pad
    bool pad_is_connected[MAX_ITEMS] = {false};

    for (size_t i = 0; i < comp->pin_count; ++i) {
        const SymbolPin* pin = &comp->pins[i];
        if (pin->type == PIN_TYPE_NOT_CONNECTED) {
            continue; // NC виводи не потребують прив'язки
        }

        bool mapping_found = false;
        for (size_t m = 0; m < comp->mapping_count; ++m) {
            if (strcmp(comp->mappings[m].symbol_pin_num, pin->number) == 0) {
                const char* target_pad = comp->mappings[m].footprint_pad_num;
                
                // Перевірка існування фізичної площадки
                bool pad_exists = false;
                for (size_t p = 0; p < comp->pad_count; ++p) {
                    if (strcmp(comp->pads[p].number, target_pad) == 0) {
                        pad_exists = true;
                        pad_is_connected[p] = true;
                        break;
                    }
                }

                if (!pad_exists) {
                    printf("[ПОМИЛКА] Пін символу %s (%s) прив'язаний до неіснуючої площадки '%s'!\n",
                           pin->number, pin->name, target_pad);
                    error_count++;
                }
                mapping_found = true;
                break;
            }
        }

        if (!mapping_found) {
            printf("[ПОМИЛКА] Пін %s (%s, тип: %s) не має маппінгу на жодну контактну площадку!\n",
                   pin->number, pin->name, pin_type_to_string(pin->type));
            error_count++;
        }
    }

    // 5. Пошук незмаплених ізольованих площадок
    for (size_t p = 0; p < comp->pad_count; ++p) {
        if (!pad_is_connected[p] && !comp->pads[p].is_mechanical) {
            printf("[ПОПЕРЕДЖЕННЯ] Контактна площадка '%s' (%s) не зв'язана зі схемою (ізольований метал)!\n",
                   comp->pads[p].number, comp->pads[p].name);
            warning_count++;
        }
    }

    printf("\nРЕЗУЛЬТАТ ВАЛІДАЦІЇ: Помилок: %d, Попереджень: %d\n", error_count, warning_count);
    if (error_count == 0) {
        printf("[СХВАЛЕНО] Компонент успішно пройшов усі тести якості.\n");
    } else {
        printf("[ЗАБЛОКОВАНО] Компонент містить критичні помилки. Імпорт відхилено.\n");
    }
    printf("=====================================================\n\n");

    return error_count;
}

int main(void) {
    ComponentDefinition comp;
    memset(&comp, 0, sizeof(comp));

    strncpy(comp.mpn, "STM32F401RET6", sizeof(comp.mpn) - 1);
    strncpy(comp.manufacturer, "STMicroelectronics", sizeof(comp.manufacturer) - 1);
    strncpy(comp.footprint_ref, "Package_QFP:LQFP-64_10x10mm_P0.5mm", sizeof(comp.footprint_ref) - 1);
    strncpy(comp.datasheet_url, "https://www.st.com/resource/en/datasheet/stm32f401re.pdf", sizeof(comp.datasheet_url) - 1);

    // Додавання пінів символу
    comp.pin_count = 3;
    strcpy(comp.pins[0].number, "1"); strcpy(comp.pins[0].name, "VBAT"); comp.pins[0].type = PIN_TYPE_POWER_IN; strcpy(comp.pins[0].unit, "A"); comp.pins[0].is_active_low = false;
    strcpy(comp.pins[1].number, "2"); strcpy(comp.pins[1].name, "PC13"); comp.pins[1].type = PIN_TYPE_BIDIRECTIONAL; strcpy(comp.pins[1].unit, "A"); comp.pins[1].is_active_low = false;
    strcpy(comp.pins[2].number, "7"); strcpy(comp.pins[2].name, "~{NRST}"); comp.pins[2].type = PIN_TYPE_INPUT; strcpy(comp.pins[2].unit, "A"); comp.pins[2].is_active_low = true;

    // Додавання площадок посадкового місця
    comp.pad_count = 3;
    strcpy(comp.pads[0].number, "1"); strcpy(comp.pads[0].name, "Pad_1"); comp.pads[0].is_mechanical = false;
    strcpy(comp.pads[1].number, "2"); strcpy(comp.pads[1].name, "Pad_2"); comp.pads[1].is_mechanical = false;
    strcpy(comp.pads[2].number, "7"); strcpy(comp.pads[2].name, "Pad_7"); comp.pads[2].is_mechanical = false;

    // Створення маппінгу
    comp.mapping_count = 3;
    strcpy(comp.mappings[0].symbol_pin_num, "1"); strcpy(comp.mappings[0].footprint_pad_num, "1");
    strcpy(comp.mappings[1].symbol_pin_num, "2"); strcpy(comp.mappings[1].footprint_pad_num, "2");
    strcpy(comp.mappings[2].symbol_pin_num, "7"); strcpy(comp.mappings[2].footprint_pad_num, "7");

    return run_component_audit(&comp) == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
