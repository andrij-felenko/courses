// вузол — це ОДНА З форм; композит тримає список того самого типу
enum Node {
    Leaf(u64),               // розмір у байтах
    Composite(Vec<Node>),    // діти того самого типу Node
}

// операція — вільна функція з ВИЧЕРПНИМ зіставленням
fn size(node: &Node) -> u64 {
    match node {
        Node::Leaf(bytes)        => *bytes,
        Node::Composite(kids)    => kids.iter().map(size).sum(),
    }
}

// ДОДАТИ ОПЕРАЦІЮ — це нова функція; НАЯВНЕ не чіпаємо:
fn count(node: &Node) -> u64 {
    match node {
        Node::Leaf(_)            => 1,
        Node::Composite(kids)    => 1 + kids.iter().map(count).sum::<u64>(),
    }
}
