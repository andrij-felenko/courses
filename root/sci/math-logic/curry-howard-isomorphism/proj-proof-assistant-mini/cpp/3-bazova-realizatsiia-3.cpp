using Context = std::map<std::string, Type>;

// Функція для порівняння типів на еквівалентність
bool typesEqual(const Type& t1, const Type& t2) {
    if (t1.index() != t2.index()) return false;
    if (auto* b1 = std::get_if<BaseType>(&t1)) {
        return b1->name == std::get<BaseType>(t2).name;
    } else {
        auto a1 = std::get<std::shared_ptr<ArrowType>>(t1);
        auto a2 = std::get<std::shared_ptr<ArrowType>>(t2);
        return typesEqual(a1->from, a2->from) && typesEqual(a1->to, a2->to);
    }
}

// Головна функція виведення типів
Type typeCheck(const Term& term, Context ctx) {
    if (auto* v = std::get_if<VarTerm>(&term)) {
        if (ctx.find(v->name) != ctx.end()) {
            return ctx[v->name];
        }
        throw std::runtime_error("Невідома гіпотеза: " + v->name);
    } 
    else if (auto* abs = std::get_if<std::shared_ptr<AbsTerm>>(&term)) {
        // Додаємо гіпотезу в контекст
        Context newCtx = ctx;
        newCtx[(*abs)->paramName] = (*abs)->paramType;
        Type bodyType = typeCheck((*abs)->body, newCtx);
        return std::make_shared<ArrowType>(ArrowType{(*abs)->paramType, bodyType});
    } 
    else if (auto* app = std::get_if<std::shared_ptr<AppTerm>>(&term)) {
        Type funcType = typeCheck((*app)->func, ctx);
        Type argType = typeCheck((*app)->arg, ctx);
        
        if (auto* arrow = std::get_if<std::shared_ptr<ArrowType>>(&funcType)) {
            if (typesEqual((*arrow)->from, argType)) {
                return (*arrow)->to;
            } else {
                throw std::runtime_error("Невідповідність типів при застосуванні Modus Ponens");
            }
        }
        throw std::runtime_error("Спроба застосувати не-імплікацію");
    }
    throw std::runtime_error("Невідомий терм");
}
