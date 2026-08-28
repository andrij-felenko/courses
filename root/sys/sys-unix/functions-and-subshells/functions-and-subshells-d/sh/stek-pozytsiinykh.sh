demonstrate_args() {
    echo "Function \$0 is: $0"
    echo "Function \$# is: $#"
    echo "Function \$1 is: $1"
    shift
    echo "After shift, \$1 is: $1"
}

# Виклик:
demonstrate_args "alpha" "beta" "gamma"
