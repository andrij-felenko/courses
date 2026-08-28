#include <stdio.h>
#include <string.h>
#include <stdbool.h>

// Суддя бачить програму як дані — її текст (код = дані):
typedef struct { const char *text; } Program;

// Суддя вгадує: чи спиниться програма, коли дати їй на вхід саму себе?
typedef bool (*Judge)(Program self, Program input);

bool always_halts(Program self, Program input) { return true;  }
bool always_loops(Program self, Program input) { return false; }
bool guess_by_text(Program self, Program input) {           // наївна статична евристика
    return strstr(input.text, "for (;;)") == NULL;          // не видно циклу — кажу «спиниться»
}

// Текст paradox подаємо явно: у C нема інтроспекції, тож код-як-дані пишемо руками.
static const Program paradox = {
    "if (guess(self, self)) for (;;);  else return;"
};

// Що paradox РОБИТЬ, коли суддя видав verdict (нескінченну гілку не запускаємо):
//   verdict=true  («спиниться»)    -> гілка for(;;) -> насправді loops
//   verdict=false («не спиниться») -> return        -> насправді halts
static const char *paradox_does(bool verdict) { return verdict ? "loops" : "halts"; }

int main(void) {
    struct { const char *name; Judge guess; } probe[] = {
        { "always_halts",  always_halts  },
        { "always_loops",  always_loops  },
        { "guess_by_text", guess_by_text },
    };
    for (int k = 0; k < 3; k++) {
        bool verdict = probe[k].guess(paradox, paradox);    // пророцтво про paradox(paradox)
        const char *predicted = verdict ? "halts" : "loops";
        const char *actual    = paradox_does(verdict);
        printf("%-13s пророчить: %-5s | paradox робить: %-5s | суддя збрехав: %s\n",
               probe[k].name, predicted, actual,
               strcmp(predicted, actual) != 0 ? "так" : "ні");
    }
    return 0;
}
