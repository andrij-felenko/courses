async def test_two_processes_diverge():
    repo = FakeRepo(); repo.seed(sample())          # СПІЛЬНА база
    a = CachedRegistry(repo, ttl_s=300)             # процес A
    b = CachedRegistry(repo, ttl_s=300)             # процес B
    await a.load_registry("home-42")                # обидва прогріли власну копію
    await b.load_registry("home-42")
    await a.rename_device("home-42", "lock-1", "вхідні двері")   # запис прийшов у процес A
    seen_a = (await a.load_registry("home-42")).devices[0].name
    seen_b = (await b.load_registry("home-42")).devices[0].name
    assert seen_a == "вхідні двері"                 # A скинув свою копію — бачить свіже
    assert seen_b == "двері"                        # B про запис не знає — віддає стару назву
    assert seen_a != seen_b                         # копії РОЗІЙШЛИСЯ
