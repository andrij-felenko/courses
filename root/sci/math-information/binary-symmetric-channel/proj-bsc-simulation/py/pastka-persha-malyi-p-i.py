# Python: ясно й ідіоматично — для розуміння й невеликих N
def until_errors(p, target=100, seed=1):
    rng = random.Random(seed)
    errors = trials = 0
    while errors < target:
        flips = (rng.random() < p) + (rng.random() < p) + (rng.random() < p)
        errors += flips >= 2
        trials += 1
    return errors / trials, trials

if __name__ == "__main__":
    p_hat, n = until_errors(0.001, target=100)
    print(f"p={0.001}  p̂={p_hat:.3e}  прогонів={n}  теорія={3*0.001**2 - 2*0.001**3:.3e}")
