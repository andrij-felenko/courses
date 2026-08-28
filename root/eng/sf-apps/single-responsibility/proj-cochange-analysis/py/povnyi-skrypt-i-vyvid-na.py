if __name__ == "__main__":
    import sys
    repo = sys.argv[1] if len(sys.argv) > 1 else "."
    commits = read_commits(repo)
    file_count, pair_count = cochange(commits)
    print(f"комітів (без merge): {len(commits)}")
    print(f"пар усього: {len(pair_count)}\n")
    print(f"{'conf':>5} {'supp':>4} {'rev':>5}   правило (міняли X → міняли й Y)")
    for conf, support, rev, src, dst in rank(file_count, pair_count):
        print(f"{conf:5.2f} {support:4d} {rev:5.2f}   {src}  ⇒  {dst}")
