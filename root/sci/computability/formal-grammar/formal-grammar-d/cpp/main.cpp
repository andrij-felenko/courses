// Обробка правила Expr = Term , { ( "+" | "-" ) , Term } ;
std::expected<double, std::string> Parser::parse_expr() {
    auto left_res = parse_term();
    if (!left_res) return left_res;
    double left = *left_res;

    while (current_.type == TokenType::Plus || current_.type == TokenType::Minus) {
        TokenType op = current_.type;
        advance();
        auto right_res = parse_term();
        if (!right_res) return right_res;
        double right = *right_res;

        if (op == TokenType::Plus) {
            left += right;
        } else {
            left -= right;
        }
    }
    return left;
}
