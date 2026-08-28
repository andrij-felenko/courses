#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libxml/xmlreader.h>

typedef struct {
    double total_uah;
    double total_usd;
    size_t count;
} StreamSummary;

/* Обробка одного вузла <tx> */
static void process_transaction(xmlTextReaderPtr reader, StreamSummary *summary) {
    xmlChar *status = xmlTextReaderGetAttribute(reader, (const xmlChar *)"status");
    if (!status || strcmp((const char *)status, "completed") != 0) {
        xmlFree(status);
        return;
    }
    xmlFree(status);

    char current_currency[8] = {0};
    double current_amount = 0.0;
    int depth = xmlTextReaderDepth(reader);

    /* Читаємо піддерево поточної транзакції до її закриття */
    while (xmlTextReaderRead(reader) == 1) {
        int node_type = xmlTextReaderNodeType(reader);
        int cur_depth = xmlTextReaderDepth(reader);

        /* Якщо повернулися на рівень вище або закрили <tx> — виходимо */
        if (cur_depth <= depth && node_type == XML_READER_TYPE_END_ELEMENT) {
            break;
        }

        if (node_type == XML_READER_TYPE_ELEMENT) {
            const xmlChar *name = xmlTextReaderConstLocalName(reader);
            if (name && strcmp((const char *)name, "amount") == 0) {
                xmlChar *curr = xmlTextReaderGetAttribute(reader, (const xmlChar *)"currency");
                if (curr) {
                    strncpy(current_currency, (const char *)curr, sizeof(current_currency) - 1);
                    xmlFree(curr);
                }
                /* Переходимо до текстового вмісту всередині <amount> */
                if (xmlTextReaderRead(reader) == 1 &&
                    xmlTextReaderNodeType(reader) == XML_READER_TYPE_TEXT) {
                    const xmlChar *val = xmlTextReaderConstValue(reader);
                    if (val) {
                        current_amount = atof((const char *)val);
                    }
                }
            }
        }
    }

    if (strcmp(current_currency, "UAH") == 0) {
        summary->total_uah += current_amount;
    } else if (strcmp(current_currency, "USD") == 0) {
        summary->total_usd += current_amount;
    }
    summary->count++;
}

int parse_stream_safe_c(const char *filepath, StreamSummary *summary) {
    /* 
     * Прапорці безпеки libxml2:
     * XML_PARSE_NONET   — заборона будь-яких мережевих запитів під час розбору
     * XML_PARSE_NODTD   — відключення завантаження зовнішнього DTD (нейтралізація XXE)
     * XML_PARSE_NOENT   — НЕ розгортати сутності автоматично
     */
    int parser_flags = XML_PARSE_NONET | XML_PARSE_NODTD | XML_PARSE_NOBLANKS;

    xmlTextReaderPtr reader = xmlReaderForFile(filepath, NULL, parser_flags);
    if (!reader) {
        fprintf(stderr, "Не вдалося відкрити XML-потік: %s\n", filepath);
        return -1;
    }

    while (xmlTextReaderRead(reader) == 1) {
        int node_type = xmlTextReaderNodeType(reader);
        if (node_type == XML_READER_TYPE_ELEMENT) {
            const xmlChar *name = xmlTextReaderConstLocalName(reader);
            if (name && strcmp((const char *)name, "tx") == 0) {
                process_transaction(reader, summary);
            }
        }
    }

    xmlFreeTextReader(reader);
    xmlCleanupParser();
    return 0;
}
