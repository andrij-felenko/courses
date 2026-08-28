import javax.swing.*;
import java.awt.*;
import java.util.function.IntConsumer;

// Справжнє подання: тільки віджети. Ні арифметики, ні умов, ні складання рядків.
final class ThermostatPanel extends JPanel implements ThermostatView {
    private final JLabel  temp   = new JLabel("", SwingConstants.CENTER);
    private final JPanel  bar    = new JPanel();
    private final JButton minus  = new JButton("−");
    private final JButton plus   = new JButton("+");
    private final JLabel  status = new JLabel("", SwingConstants.CENTER);

    public void showTemperature(String text) { temp.setText(text); }
    public void showBarColor(String hex)     { bar.setBackground(Color.decode(hex)); }
    public void setMinusEnabled(boolean on)  { minus.setEnabled(on); }
    public void setPlusEnabled(boolean on)   { plus.setEnabled(on); }
    public void showStatus(String text)      { status.setText(text); }

    public void onNudge(IntConsumer handler) {
        minus.addActionListener(e -> handler.accept(-1));
        plus.addActionListener(e -> handler.accept(+1));
    }
}
