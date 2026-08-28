inner_func() {
    # 'token' не оголошено тут як local
    echo "inner_func reads token: $token"
    token="modified_by_inner" # Змінює локальну змінну outer_func!
}

outer_func() {
    local token="secret_auth_key"
    inner_func
    echo "outer_func token is now: $token"
}

token="global_default"
outer_func
echo "global token is: $token"
