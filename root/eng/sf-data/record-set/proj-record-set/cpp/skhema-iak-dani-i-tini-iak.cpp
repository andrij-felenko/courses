enum class RowState : uint8_t {
    Unchanged,   // прочитаний і не чіпаний
    Modified,    // правлений; початкові значення лежать в orig_
    Added,       // доданий тут, у базі його ще немає
    Deleted,     // позначений вилученим, лишається на місці надгробком
    Discarded    // доданий і тут-таки вилучений — у базу не піде нічого
};

using Value = std::variant<std::monostate, int64_t, std::string>;  // monostate — це NULL

struct SvHash {                        // щоб пошук за string_view не створював std::string
    using is_transparent = void;
    size_t operator()(std::string_view s) const noexcept {
        return std::hash<std::string_view>{}(s);
    }
};

// рядок і колонка, склеєні в один ключ: до 65 536 колонок і до 2⁴⁸ рядків
inline uint64_t cell_key(size_t row, size_t colno) {
    return (static_cast<uint64_t>(row) << 16) | static_cast<uint64_t>(colno);
}

struct KeyBook {                       // тимчасовий ключ → справжній, виданий базою
    int64_t next_temp = -1;
    std::unordered_map<int64_t, int64_t> real;

    int64_t issue() { return next_temp--; }

    int64_t resolve(int64_t v) const {
        if (v >= 0) return v;                       // справжній ключ, нічого робити
        const auto it = real.find(v);
        if (it == real.end())
            throw std::logic_error("батьківський рядок ще не вставлено");
        return it->second;
    }
};

struct Statement;                      // оголошення наперед: тіла — далі за текстом
struct RowSource;
struct Op;
enum class Phase : uint8_t { Insert, Update, Delete };

class RecordSet {
public:
    RecordSet(std::string table, std::vector<Column> cols,
              std::vector<std::string> key, KeyBook& keys)
        : table_(std::move(table)), cols_(std::move(cols)),
          key_(std::move(key)), keys_(&keys) {
        for (size_t c = 0; c < cols_.size(); ++c) index_.emplace(cols_[c].name, c);
    }

    size_t rows() const noexcept { return nrows_; }

    size_t col(std::string_view name) const {
        const auto it = index_.find(name);
        if (it == index_.end())
            throw std::out_of_range("немає колонки " + std::string(name));
        return it->second;
    }

    void   reserve(size_t n);
    void   load(RowSource& src, size_t expect);

    bool                            is_null (size_t r, size_t c) const;
    std::optional<int64_t>          get_int (size_t r, size_t c) const;
    std::optional<std::string_view> get_text(size_t r, size_t c) const;

    void   set_int (size_t r, size_t c, std::optional<int64_t> v);
    void   set_text(size_t r, size_t c, std::optional<std::string> v);
    size_t append_row();
    void   erase_row(size_t r);

    void      collect(std::vector<Op>& plan, Phase phase);
    Statement make(size_t r, Phase phase) const;
    void      note_key(size_t r, const std::vector<Value>& returned);
    void      accept();

private:
    size_t      grow_one();
    Value       value_at(size_t r, size_t c) const;
    Value       param_at(size_t r, size_t c) const;
    Value       original_at(size_t r, size_t c) const;
    void        remember(size_t r, size_t c);
    std::string where_original(size_t r, std::vector<Value>& params) const;
    Statement   make_insert(size_t r) const;
    Statement   make_update(size_t r) const;
    Statement   make_delete(size_t r) const;
    void        compact();

    std::string                                                      table_;
    std::vector<Column>                                              cols_;
    std::vector<std::string>                                         key_;
    KeyBook*                                                         keys_;
    std::vector<RowState>                                            state_;
    std::unordered_map<std::string, size_t, SvHash, std::equal_to<>> index_;
    std::unordered_map<uint64_t, Value>                              orig_;
    size_t                                                           nrows_ = 0;
};
