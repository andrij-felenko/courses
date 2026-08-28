typedef struct {
    gpio_num_t  en_pin;     // EN load switch-а гілки (1 = гілка під живленням)
    const char *name;
} power_branch_t;

static const power_branch_t BRANCHES[] = {
    { SENSOR_LOADSW_EN,  "sensor"  },
    { RADIO_LOADSW_EN,   "radio"   },
    { DISPLAY_LOADSW_EN, "display" },
};
#define BRANCH_LEN (sizeof(BRANCHES) / sizeof(BRANCHES[0]))

static void all_branches_off(void)
{
    for (size_t i = 0; i < BRANCH_LEN; i++)
        gpio_set_level(BRANCHES[i].en_pin, 0);
}
