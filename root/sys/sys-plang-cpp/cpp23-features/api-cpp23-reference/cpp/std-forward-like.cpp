namespace std {

template <class Owner, class Member>
constexpr auto&& forward_like(Member&& member) noexcept {
    using UnrefOwner = remove_reference_t<Owner>;
    using UnrefMember = remove_reference_t<Member>;

    if constexpr (is_const_v<UnrefOwner>) {
        if constexpr (is_rvalue_reference_v<Owner>) {
            return static_cast<const UnrefMember&&>(member);
        } else {
            return static_cast<const UnrefMember&>(member);
        }
    } else {
        if constexpr (is_rvalue_reference_v<Owner>) {
            return static_cast<UnrefMember&&>(member);
        } else {
            return static_cast<UnrefMember&>(member);
        }
    }
}

} // namespace std
