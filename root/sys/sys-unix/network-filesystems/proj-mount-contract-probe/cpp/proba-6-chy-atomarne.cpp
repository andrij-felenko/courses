static void probe_excl_race() {
    constexpr int ROUNDS = 400;
    std::string prefix = std::format("race-{}", ::getpid());
    std::string req = std::format("RACE {} {}", prefix, ROUNDS);
    if (send_line(req) < 0) return;

    std::string mine;
    mine.reserve(ROUNDS);
    for (int i = 0; i < ROUNDS; ++i) {
        auto name = at(std::format("{}-{}", prefix, i));
        int fd = ::open(name.c_str(), O_WRONLY | O_CREAT | O_EXCL, 0644);
        if (fd >= 0) { mine.push_back('1'); ::close(fd); }
        else { mine.push_back('0'); }
    }

    std::string theirs;
    if (recv_line(theirs) < 0) return;
    if (theirs.size() != static_cast<size_t>(ROUNDS)) { std::cout << "6. мапа не тієї довжини\n"; return; }

    int mine_won = 0, their_won = 0, both = 0, none = 0;
    for (int i = 0; i < ROUNDS; ++i) {
        bool m = (mine[i] == '1'), t = (theirs[i] == '1');
        mine_won += m;
        their_won += t;
        both += (m && t);
        none += (!m && !t);
    }

    std::cout << std::format("6.  O_EXCL, {} кіл: наших {}, чужих {}, ПОДВІЙНИХ {}, нічиїх {}\n",
                ROUNDS, mine_won, their_won, both, none);
    if (both) std::cout << "    подвійна перемога = створення НЕ атомарне між машинами\n";
    if (mine_won == 0 || their_won == 0) std::cout << "    забіги не перетнулися в часі — проба нічого не перевірила\n";

    std::error_code ec;
    for (int i = 0; i < ROUNDS; ++i) {
        fs::remove(at(std::format("{}-{}", prefix, i)), ec);
    }
}

int main(int argc, char **argv) {
    if (argc == 4 && std::string_view(argv[1]) == "writer") {
        share_dir = argv[2];
        ctl = tcp_accept(argv[3]);
        if (ctl < 0) { std::perror("accept"); return 1; }
        serve();
        return 0;
    }
    if (argc == 5 && std::string_view(argv[1]) == "reader") {
        share_dir = argv[2];
        ctl = tcp_connect(argv[3], argv[4]);
        if (ctl < 0) { std::perror("connect"); return 1; }
        probe_visibility();
        probe_open_file();
        probe_write_path();
        probe_locks();
        probe_open_unlink();
        probe_excl_race();
        send_line("BYE");
        return 0;
    }
    std::cerr << std::format("вжиток:\n  {} writer <спільний-каталог> <порт>\n  {} reader <спільний-каталог> <хост-письменника> <порт>\n",
                argv[0], argv[0]);
    return 1;
}
