/* Local KWin 6 shortcuts; independent of Krohnkite and the current layout. */
"use strict";

function moveWindowAndFollow(index) {
    var window = workspace.activeWindow;
    var target = workspace.desktops[index];
    if (!window || !target || window.deleted || !window.moveable
        || (!window.normalWindow && !window.dialog)) {
        return;
    }

    window.desktops = [target];
    // Respect rules that prevent a window from leaving its assigned desktop.
    if (window.desktops.length !== 1 || window.desktops[0] !== target) {
        return;
    }

    workspace.currentDesktop = target;
    workspace.activeWindow = window;
}

// Resolve targets from the current ordered list on every press. Adding,
// removing, or reordering desktops must not leave shortcuts tied to old IDs.
for (var index = 0; index < 9; ++index) {
    (function (desktopIndex) {
        registerShortcut(
            "Move Window and Follow Desktop " + (desktopIndex + 1),
            "Mover ventana y seguir al escritorio " + (desktopIndex + 1),
            "",
            function () { moveWindowAndFollow(desktopIndex); }
        );
    })(index);
}

registerShortcut(
    "Create Desktop and Follow",
    "Crear escritorio y cambiar a él",
    "Meta+Ctrl+D",
    function () {
        var position = workspace.desktops.length;
        workspace.createDesktop(position, "");
        // At KWin's desktop limit creation can fail; do not change desktops.
        if (workspace.desktops.length > position) {
            workspace.currentDesktop = workspace.desktops[position];
        }
    }
);
