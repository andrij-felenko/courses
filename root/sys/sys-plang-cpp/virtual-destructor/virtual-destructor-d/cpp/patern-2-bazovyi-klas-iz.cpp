class PolymorphicEntity {
public:
    virtual ~PolymorphicEntity() = default;

    PolymorphicEntity(const PolymorphicEntity&) = default;
    PolymorphicEntity& operator=(const PolymorphicEntity&) = default;
    PolymorphicEntity(PolymorphicEntity&&) noexcept = default;
    PolymorphicEntity& operator=(PolymorphicEntity&&) noexcept = default;

    virtual void update() = 0;
};
