int read_sensor_data(void __iomem *hw_regs, void __user *user_buf) {
    // ПОМИЛКА: Пряме розіменування __iomem
    // Sparse скаже: dereference of noderef expression
    int val = *(int __iomem *)hw_regs; 
    
    // ПОМИЛКА: Пряме розіменування __user
    // Sparse скаже: dereference of noderef expression
    ((int __user *)user_buf)[0] = val; 
    return 0;
}
