type Node =
  | { op: "num"; value: number }
  | { op: "var"; name: string }
  | { op: "add"; left: Node; right: Node }
  | { op: "mul"; left: Node; right: Node };

function evalNode(n: Node, env: Map<string, number>): number {
  switch (n.op) {
    case "num": return n.value;
    case "var": return env.get(n.name)!;
    case "add": return evalNode(n.left, env) + evalNode(n.right, env);
    case "mul": return evalNode(n.left, env) * evalNode(n.right, env);
  }
}
