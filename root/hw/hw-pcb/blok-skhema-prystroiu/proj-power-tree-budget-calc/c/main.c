#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_CHILDREN 8
#define MAX_NODES 32

typedef enum {
    NODE_ROOT_SOURCE,
    NODE_BUCK_CONVERTER,
    NODE_BOOST_CONVERTER,
    NODE_LDO_REGULATOR,
    NODE_ISOLATED_DCDC,
    NODE_LEAF_LOAD
} node_type_t;

typedef struct power_node {
    int id;
    const char *name;
    node_type_t type;
    float v_out;                 /* Вихідна напруга, В */
    float i_leaf_load;           /* Власний струм споживання (для листових вузлів), А */
    float i_max_limit;           /* Паспортний ліміт вихідного струму, А */
    float efficiency_nominal;    /* Номінальний ККД для DC-DC (0.0 .. 1.0) */
    float theta_ja;              /* Тепловий опір кристал-середовище, °C/Вт */
    float t_j_max;               /* Максимально допустима температура кристала, °C */

    struct power_node *parent;
    struct power_node *children[MAX_CHILDREN];
    size_t children_count;

    /* Розрахункові вихідні поля */
    float calculated_i_out;      /* Сумарний струм на виході вузла, А */
    float calculated_p_out;      /* Корисна вихідна потужність, Вт */
    float calculated_efficiency; /* Розрахунковий ККД */
    float calculated_p_in;       /* Вхідна споживана потужність, Вт */
    float calculated_i_in;       /* Вхідний струм споживання, А */
    float calculated_p_loss;     /* Потужність теплових втрат, Вт */
    float calculated_t_j;        /* Розрахункова температура кристала, °C */
    bool has_overcurrent_error;
    bool has_overheat_error;
} power_node_t;

static power_node_t* create_node(int id, const char *name, node_type_t type, 
                                 float v_out, float i_leaf, float i_limit, 
                                 float eff, float theta, float tj_max) {
    power_node_t *node = (power_node_t*)malloc(sizeof(power_node_t));
    if (!node) return NULL;
    memset(node, 0, sizeof(power_node_t));

    node->id = id;
    node->name = name;
    node->type = type;
    node->v_out = v_out;
    node->i_leaf_load = i_leaf;
    node->i_max_limit = i_limit;
    node->efficiency_nominal = eff;
    node->theta_ja = theta;
    node->t_j_max = tj_max;

    return node;
}

static bool add_child(power_node_t *parent, power_node_t *child) {
    if (!parent || !child || parent->children_count >= MAX_CHILDREN) {
        return false;
    }
    parent->children[parent->children_count++] = child;
    child->parent = parent;
    return true;
}

static float evaluate_converter_efficiency(const power_node_t *node, float i_out) {
    if (node->type == NODE_LDO_REGULATOR) {
        if (node->parent && node->parent->v_out > 0.01f) {
            return node->v_out / node->parent->v_out;
        }
        return 0.5f;
    }

    if (node->type == NODE_BUCK_CONVERTER || node->type == NODE_BOOST_CONVERTER || 
        node->type == NODE_ISOLATED_DCDC) {
        if (i_out <= 0.001f) return 0.20f; /* Низький ККД на холостому ході */
        
        float load_ratio = i_out / (node->i_max_limit > 0.01f ? node->i_max_limit : 1.0f);
        if (load_ratio > 1.0f) load_ratio = 1.0f;

        /* Модель нелінійності ККД: плавний вихід на плато з падінням при малому струмі */
        float eff = node->efficiency_nominal * (1.0f - 0.15f * (1.0f - load_ratio) * (1.0f - load_ratio));
        return (eff > 0.1f) ? eff : 0.1f;
    }

    return 1.0f;
}

static void calculate_power_tree_recursive(power_node_t *node, float ambient_temp) {
    if (!node) return;

    /* Рекурсивно обчислюємо всіх нащадків (Bottom-Up) */
    float sum_child_current = 0.0f;
    for (size_t i = 0; i < node->children_count; ++i) {
        calculate_power_tree_recursive(node->children[i], ambient_temp);
        sum_child_current += node->children[i]->calculated_i_in;
    }

    if (node->type == NODE_LEAF_LOAD) {
        node->calculated_i_out = node->i_leaf_load;
        node->calculated_p_out = node->v_out * node->calculated_i_out;
        node->calculated_efficiency = 1.0f;
        node->calculated_p_in = node->calculated_p_out;
        node->calculated_i_in = node->calculated_i_out;
        node->calculated_p_loss = 0.0f;
        node->calculated_t_j = ambient_temp;
        node->has_overcurrent_error = false;
        node->has_overheat_error = false;
        return;
    }

    node->calculated_i_out = sum_child_current;
    node->calculated_p_out = node->v_out * node->calculated_i_out;
    node->has_overcurrent_error = (node->i_max_limit > 0.0f && node->calculated_i_out > node->i_max_limit);

    if (node->type == NODE_ROOT_SOURCE) {
        node->calculated_efficiency = 1.0f;
        node->calculated_p_in = node->calculated_p_out;
        node->calculated_i_in = node->calculated_i_out;
        node->calculated_p_loss = 0.0f;
        node->calculated_t_j = ambient_temp;
        node->has_overheat_error = false;
        return;
    }

    /* Розрахунок перетворювача */
    float v_in = node->parent ? node->parent->v_out : node->v_out;
    node->calculated_efficiency = evaluate_converter_efficiency(node, node->calculated_i_out);

    if (node->type == NODE_LDO_REGULATOR) {
        node->calculated_p_loss = (v_in - node->v_out) * node->calculated_i_out;
        node->calculated_p_in = node->calculated_p_out + node->calculated_p_loss;
        node->calculated_i_in = node->calculated_i_out;
    } else {
        node->calculated_p_in = (node->calculated_efficiency > 0.01f) 
                                ? (node->calculated_p_out / node->calculated_efficiency) 
                                : node->calculated_p_out;
        node->calculated_p_loss = node->calculated_p_in - node->calculated_p_out;
        node->calculated_i_in = (v_in > 0.01f) ? (node->calculated_p_in / v_in) : 0.0f;
    }

    node->calculated_t_j = ambient_temp + (node->calculated_p_loss * node->theta_ja);
    node->has_overheat_error = (node->calculated_t_j > node->t_j_max);
}

static void print_node_report(const power_node_t *node, int depth) {
    if (!node) return;

    char indent[64] = {0};
    for (int i = 0; i < depth && i < 30; ++i) {
        strcat(indent, "  ");
    }

    const char *type_str = "LOAD";
    if (node->type == NODE_ROOT_SOURCE)      type_str = "ROOT";
    else if (node->type == NODE_BUCK_CONVERTER)   type_str = "BUCK";
    else if (node->type == NODE_BOOST_CONVERTER)  type_str = "BOOST";
    else if (node->type == NODE_LDO_REGULATOR)    type_str = "LDO";
    else if (node->type == NODE_ISOLATED_DCDC)    type_str = "ISO-DC";

    printf("%s[%s] %-20s | %4.1fV | I_out: %5.3fA | P_out: %5.2fW | ККД: %4.1f%% | P_loss: %5.2fW | T_j: %5.1fC",
           indent, type_str, node->name, node->v_out, node->calculated_i_out,
           node->calculated_p_out, node->calculated_efficiency * 100.0f,
           node->calculated_p_loss, node->calculated_t_j);

    if (node->has_overcurrent_error) printf(" -> [УВАГА: СТРУМ > ЛІМІТ!]");
    if (node->has_overheat_error)    printf(" -> [УВАГА: ПЕРЕГРІВ КРИСТАЛА!]");
    printf("\n");

    for (size_t i = 0; i < node->children_count; ++i) {
        print_node_report(node->children[i], depth + 1);
    }
}

static void free_tree(power_node_t *node) {
    if (!node) return;
    for (size_t i = 0; i < node->children_count; ++i) {
        free_tree(node->children[i]);
    }
    free(node);
}

int main(void) {
    const float ambient_temperature = 60.0f; /* Промисловий діапазон +60 °C */

    /* 1. Створення вузлів дерева живлення */
    power_node_t *root = create_node(1, "Primary 24V DC", NODE_ROOT_SOURCE, 24.0f, 0.0f, 5.0f, 1.0f, 0.0f, 125.0f);
    power_node_t *buck_5v = create_node(2, "Buck 24V->5V", NODE_BUCK_CONVERTER, 5.0f, 0.0f, 2.5f, 0.91f, 35.0f, 125.0f);

    power_node_t *buck_3v3 = create_node(3, "Buck 5V->3.3V", NODE_BUCK_CONVERTER, 3.3f, 0.0f, 1.5f, 0.94f, 45.0f, 125.0f);
    power_node_t *buck_1v2 = create_node(4, "Buck 5V->1.2V Core", NODE_BUCK_CONVERTER, 1.2f, 0.0f, 1.2f, 0.88f, 50.0f, 125.0f);
    power_node_t *ldo_3v3a = create_node(5, "LDO 5V->3.3V_ANA", NODE_LDO_REGULATOR, 3.3f, 0.0f, 0.2f, 0.66f, 62.0f, 125.0f);
    power_node_t *iso_5v   = create_node(6, "ISO DC-DC 5V->5V", NODE_ISOLATED_DCDC, 5.0f, 0.0f, 0.3f, 0.78f, 70.0f, 125.0f);

    /* Листові навантаження 3.3V */
    power_node_t *load_mcu_io = create_node(7, "MCU I/O & Periph", NODE_LEAF_LOAD, 3.3f, 0.120f, 0.0f, 1.0f, 0.0f, 105.0f);
    power_node_t *load_flash  = create_node(8, "QSPI Flash 32MB",  NODE_LEAF_LOAD, 3.3f, 0.045f, 0.0f, 1.0f, 0.0f, 105.0f);
    power_node_t *load_eth    = create_node(9, "Ethernet PHY",     NODE_LEAF_LOAD, 3.3f, 0.180f, 0.0f, 1.0f, 0.0f, 105.0f);

    /* Листові навантаження 1.2V Core */
    power_node_t *load_core   = create_node(10, "MCU Cortex-M7 Core", NODE_LEAF_LOAD, 1.2f, 0.850f, 0.0f, 1.0f, 0.0f, 105.0f);

    /* Листові навантаження 3.3V Analog */
    power_node_t *load_adc    = create_node(11, "24-bit Delta-Sigma ADC", NODE_LEAF_LOAD, 3.3f, 0.015f, 0.0f, 1.0f, 0.0f, 105.0f);
    power_node_t *load_opamp  = create_node(12, "Input Buffer Op-Amps",   NODE_LEAF_LOAD, 3.3f, 0.025f, 0.0f, 1.0f, 0.0f, 105.0f);
    power_node_t *load_vref   = create_node(13, "Precision 2.5V VREF",    NODE_LEAF_LOAD, 3.3f, 0.005f, 0.0f, 1.0f, 0.0f, 105.0f);

    /* Листові навантаження 5V Isolated */
    power_node_t *load_can    = create_node(14, "CAN-FD Transceiver", NODE_LEAF_LOAD, 5.0f, 0.060f, 0.0f, 1.0f, 0.0f, 105.0f);
    power_node_t *load_rs485  = create_node(15, "RS-485 Modbus Node", NODE_LEAF_LOAD, 5.0f, 0.080f, 0.0f, 1.0f, 0.0f, 105.0f);

    /* 2. Побудова ієрархії зв'язків */
    add_child(root, buck_5v);

    add_child(buck_5v, buck_3v3);
    add_child(buck_5v, buck_1v2);
    add_child(buck_5v, ldo_3v3a);
    add_child(buck_5v, iso_5v);

    add_child(buck_3v3, load_mcu_io);
    add_child(buck_3v3, load_flash);
    add_child(buck_3v3, load_eth);

    add_child(buck_1v2, load_core);

    add_child(ldo_3v3a, load_adc);
    add_child(ldo_3v3a, load_opamp);
    add_child(ldo_3v3a, load_vref);

    add_child(iso_5v, load_can);
    add_child(iso_5v, load_rs485);

    /* 3. Розрахунок бюджету дерева живлення */
    calculate_power_tree_recursive(root, ambient_temperature);

    /* 4. Вивід звіту */
    printf("========================================================================================\n");
    printf("         ІНЖЕНЕРНИЙ ЗВІТ РОЗРАХУНКУ ДЕРЕВА ЖИВЛЕННЯ ТА ТЕПЛОВОГО БАЛАНСУ (C99)          \n");
    printf("         Температура середовища T_amb = %.1f °C                                         \n", ambient_temperature);
    printf("========================================================================================\n");
    print_node_report(root, 0);
    printf("========================================================================================\n");
    printf("Підсумок: Вхідна потужність = %.2f Вт | Вхідний струм від 24V = %.3f А | Втрати = %.2f Вт\n",
           root->calculated_p_in, root->calculated_i_in, root->calculated_p_in - (buck_3v3->calculated_p_out + buck_1v2->calculated_p_out + ldo_3v3a->calculated_p_out + iso_5v->calculated_p_out));
    printf("========================================================================================\n");

    free_tree(root);
    return 0;
}
