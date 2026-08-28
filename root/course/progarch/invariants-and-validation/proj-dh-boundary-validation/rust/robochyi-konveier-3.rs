#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn valid_input_becomes_trusted_command() {
        let cmd = parse_command(r#"{"deviceId":"kitchen-1","targetTemp":21.5,"action":"heat"}"#)
            .expect("валідний вхід має пройти");
        assert_eq!(cmd.target.value(), 21.5);
        assert_eq!(cmd.action, Action::Heat);
    }

    #[test]
    fn three_failures_give_full_list() {
        let errs = parse_command(r#"{"deviceId":"","targetTemp":2000,"action":"melt"}"#)
            .expect_err("кривий вхід має відпасти");
        assert_eq!(errs.len(), 3);                    // усі три, не перша-ліпша
    }

    #[test]
    fn partial_validity_yields_no_command() {
        let errs = parse_command(r#"{"deviceId":"kitchen-1","targetTemp":2000,"action":"heat"}"#)
            .unwrap_err();
        assert_eq!(errs.len(), 1);                     // одне погане поле губить усю команду
        assert_eq!(errs[0].field, "targetTemp");
    }
}
