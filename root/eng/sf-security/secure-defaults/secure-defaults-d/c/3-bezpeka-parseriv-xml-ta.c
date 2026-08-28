#include <libxml/parser.h>

/* Безпечна ініціалізація парсера libxml2 з відключенням мережі та сутностей */
xmlParserCtxtPtr create_secure_xml_parser(void) {
    xmlParserCtxtPtr ctxt = xmlNewParserCtxt();
    if (!ctxt) return NULL;
    
    /* Заборона завантаження зовнішніх DTD та резолвінгу сутностей */
    int options = XML_PARSE_NONET | XML_PARSE_NODICT | XML_PARSE_NOENT;
    xmlCtxtUseOptions(ctxt, options);
    return ctxt;
}
