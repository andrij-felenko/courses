#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_NAME_LEN 64
#define MAX_PINS 256

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

typedef struct {
    int logical_number;
    char name[MAX_NAME_LEN];
    PinType type;
    bool is_active_low;
} SymbolPin;

typedef struct {
    int pad_number;
    char physical_name[MAX_NAME_LEN];
} FootprintPad;

typedef struct {
    int symbol_pin_num;
    int footprint_pad_num;
} PinToPadMapping;

typedef struct {
    char mpn[MAX_NAME_LEN];
    char manufacturer[MAX_NAME_LEN];
    char footprint_name[MAX_NAME_LEN];
    char datasheet_url[128];
    
    SymbolPin pins[MAX_PINS];
    size_t pin_count;
    
    FootprintPad pads[MAX_PINS];
    size_t pad_count;
    
    PinToPadMapping mappings[MAX_PINS];
    size_t mapping_count;
} AtomicComponent;

// Валідація бієкції: кожен логічний пін мусить мати рівно одну фізичну площадку
bool validate_atomic_component(const AtomicComponent* comp) {
    if (comp->pin_count == 0 || comp->pad_count == 0) {
        fprintf(stderr, "[ПОМИЛКА] Компонент %s не містить виводів або площадок.\n", comp->mpn);
        return false;
    }
    
    if (strlen(comp->mpn) == 0 || strlen(comp->manufacturer) == 0) {
        fprintf(stderr, "[ПОМИЛКА] Відсутні обов'язкові атрибути BOM (MPN / Manufacturer).\n");
        return false;
    }
    
    bool mapped_pads[MAX_PINS] = {false};
    
    for (size_t i = 0; i < comp->pin_count; ++i) {
        int pin_num = comp->pins[i].logical_number;
        bool found = false;
        
        for (size_t j = 0; j < comp->mapping_count; ++j) {
            if (comp->mappings[j].symbol_pin_num == pin_num) {
                int pad_num = comp->mappings[j].footprint_pad_num;
                if (pad_num <= 0 || pad_num > (int)comp->pad_count) {
                    fprintf(stderr, "[ПОМИЛКА] Пін %d змаплений на неіснуючу площадку %d.\n", pin_num, pad_num);
                    return false;
                }
                mapped_pads[pad_num - 1] = true;
                found = true;
                break;
            }
        }
        
        if (!found && comp->pins[i].type != PIN_TYPE_NOT_CONNECTED) {
            fprintf(stderr, "[ПОМИЛКА] Пін %d (%s) не має прив'язаної контактної площадки!\n",
                    pin_num, comp->pins[i].name);
            return false;
        }
    }
    
    return true;
}
