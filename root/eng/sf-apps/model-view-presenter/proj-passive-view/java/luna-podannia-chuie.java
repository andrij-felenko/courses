final class TargetField {                      // усередині подання
    private final JTextField field = new JTextField();
    private boolean pushing = false;           // «зараз пишу я, а не людина»

    void show(String text) {
        pushing = true;
        try { field.setText(text); }
        finally { pushing = false; }
    }

    void onTyped(Consumer<String> handler) {
        field.getDocument().addDocumentListener(new TextChangeListener(() -> {
            if (!pushing) handler.accept(field.getText());   // луну назовні не пускаємо
        }));
    }
}
