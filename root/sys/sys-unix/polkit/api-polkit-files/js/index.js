polkit.addRule(function (action, subject) {
    if (action.id.indexOf("org.freedesktop.udisks2.") === 0 &&
        action.lookup("drive.removable") === "true" &&
        subject.isInGroup("storage") && subject.local && subject.active) {
        polkit.log("udisks дозволено для " + subject.user);
        return polkit.Result.YES;
    }
});
polkit.addAdminRule(function (action, subject) {
    return ["unix-group:wheel"];
});
