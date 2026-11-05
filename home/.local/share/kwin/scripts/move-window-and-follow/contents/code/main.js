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

for (var index = 0; index < 4; ++index) {
    (function (desktopIndex) {
        registerShortcut(
            "Move Window and Follow Desktop " + (desktopIndex + 1),
            "Mover ventana y seguir al escritorio " + (desktopIndex + 1),
            "",
            function () { moveWindowAndFollow(desktopIndex); }
        );
    })(index);
}
