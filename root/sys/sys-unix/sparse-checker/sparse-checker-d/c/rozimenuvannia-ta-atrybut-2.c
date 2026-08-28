int read_sensor_data(void __iomem *hw_regs, void __user *user_buf) {
    // БЕЗПЕЧНО: використання спеціальної функції доступу
    int val = readl(hw_regs); 
    
    // БЕЗПЕЧНО: копіювання через "міст"
    if (copy_to_user(user_buf, &val, sizeof(val))) {
        return -EFAULT;
    }
    return 0;
}
