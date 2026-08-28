struct Node {
    int         value;
    const Node* next;   // хвіст — спільний, той самий для старого й нового
};

// "prepend" не копіює хвіст — лише чіпляє нову голову перед ним
const Node* prepend(int v, const Node* tail) {
    return new Node{ v, tail };   // один новий вузол; решта — спільна
}

const Node* a = prepend(3, prepend(2, prepend(1, nullptr)));  // [3,2,1]
const Node* b = prepend(9, a);                                // [9,3,2,1]
// a досі [3,2,1] і ЖИВИЙ; b лише додав один вузол перед спільним хвостом a
