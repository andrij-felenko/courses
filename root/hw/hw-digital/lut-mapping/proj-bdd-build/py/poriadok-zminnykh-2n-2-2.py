    def size(self, root):
        seen, stack = set(), [root]
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u)
            if u > TRUE:
                _, lo, hi = self.node[u]
                stack += [lo, hi]
        return len(seen)
