#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

typedef enum {
    PARSER_SEARCH_PROMPT,
    PARSER_IN_IPD_HEADER,
    PARSER_SKIP_IPD_BODY
} IpdParserState;

typedef struct {
    IpdParserState state;
    uint16_t ipd_bytes_left;
    uint8_t prev_byte;
} SafePromptParser;

void parser_init(SafePromptParser* parser) {
    parser->state = PARSER_SEARCH_PROMPT;
    parser->ipd_bytes_left = 0;
    parser->prev_byte = 0;
}

bool parse_byte_for_prompt(SafePromptParser* parser, uint8_t byte) {
    if (parser->state == PARSER_SKIP_IPD_BODY) {
        if (--parser->ipd_bytes_left == 0) {
            parser->state = PARSER_SEARCH_PROMPT;
        }
        parser->prev_byte = byte;
        return false;
    }

    if (parser->prev_byte == '>' && byte == ' ') {
        parser->prev_byte = 0;
        return true; // Валідовано точний інлайн-промпт '> '
    }

    parser->prev_byte = byte;
    return false;
}
