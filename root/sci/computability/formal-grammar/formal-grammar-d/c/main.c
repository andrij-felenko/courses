/* Обробка правила <Expr> ::= <Term> { ("+" | "-") <Term> } */
double parse_expr(Parser *p) {
    double left = parse_term(p);

    while (p->current.type == TOK_PLUS || p->current.type == TOK_MINUS) {
        TokenType op = p->current.type;
        next_token(p);
        double right = parse_term(p);

        if (op == TOK_PLUS) {
            left += right;
        } else {
            left -= right;
        }
    }
    return left;
}
