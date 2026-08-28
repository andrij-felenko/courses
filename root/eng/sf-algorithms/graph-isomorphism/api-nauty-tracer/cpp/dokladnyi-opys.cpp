// У C++ структура використовується через extern "C" або виклик з заголовків nauty.h:
extern "C" {
#include "nauty.h"
}

// У C++ об'єкт налаштувань ініціалізується макросом:
optionblk options;
DEFAULTOPTIONS_GRAPH(&options);
options.getcanon = TRUE;
options.writeautoms = FALSE;
