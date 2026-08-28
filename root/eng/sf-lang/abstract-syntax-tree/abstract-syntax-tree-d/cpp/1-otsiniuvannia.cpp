double evaluate(const ASTNode* node) {
    if (auto num = dynamic_cast<const NumberNode*>(node)) {
        return num->value; // Листок: повертаємо число
    }
    if (auto bin = dynamic_cast<const BinaryOpNode*>(node)) {
        double left_val  = evaluate(bin->left.get());  // Обчислюємо ліве піддерево
        double right_val = evaluate(bin->right.get()); // Обчислюємо праве піддерево
        
        switch (bin->op) {
            case '+': return left_val + right_val;
            case '-': return left_val - right_val;
            case '*': return left_val * right_val;
            case '/': return left_val / right_val;
        }
    }
    return 0.0;
}
