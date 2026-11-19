/* Local KWin 6 helper. Krohnkite remains responsible for floating/tiling state.
 * This setup uses Krohnkite's default layers: tiled=below, floating=normal. */
"use strict";

var records = {};
var requestInFlight = false;
var requestSerial = 0;
var pendingRequest = null;
var preferredWidth = Number(readConfig("floatingWidth", 0));
var preferredHeight = Number(readConfig("floatingHeight", 0));
var requestTimeout = new QTimer();
requestTimeout.singleShot = true;
requestTimeout.timeout.connect(function () {
    if (pendingRequest) pendingRequest.cancel();
    requestInFlight = false;
    ++requestSerial;
});

function copySize(geometry) {
    return { width: geometry.width, height: geometry.height };
}

function floatingGeometry(before, remembered, area, minimum, maximum) {
    // An explicit reference size replaces the compact initial-size heuristic.
    // Manual floating sizes still take precedence on subsequent toggles.
    var width = remembered ? remembered.width : preferredWidth > 0 ? preferredWidth
        : Math.min(before.width, area.width * 0.70, 1280);
    var height = remembered ? remembered.height : preferredHeight > 0 ? preferredHeight
        : Math.min(before.height, area.height * 0.70, 900);
    var minWidth = Math.max(1, minimum.width);
    var minHeight = Math.max(1, minimum.height);
    var maxWidth = maximum.width > 0 ? maximum.width : area.width;
    var maxHeight = maximum.height > 0 ? maximum.height : area.height;
    width = Math.round(Math.max(minWidth, Math.min(width, area.width, maxWidth)));
    height = Math.round(Math.max(minHeight, Math.min(height, area.height, maxHeight)));
    return {
        x: Math.round(area.x + (area.width - width) / 2),
        y: Math.round(area.y + (area.height - height) / 2),
        width: width,
        height: height
    };
}

function cancelCorrection(record) {
    var job = record.job;
    if (!job) return;
    record.job = null;
    job.timer.stop();
    try {
        job.window.frameGeometryChanged.disconnect(job.centerActualSize);
        job.window.interactiveMoveResizeStarted.disconnect(job.cancel);
    } catch (error) {
        // KWin may already be destroying a window when windowRemoved arrives.
    }
}

function recordFor(window) {
    var key = String(window.internalId);
    if (!records[key]) {
        var record = { size: null, job: null };
        records[key] = record;
        window.interactiveMoveResizeFinished.connect(function () {
            if (!window.deleted && !window.keepBelow && !window.fullScreen && !window.maximizeMode)
                record.size = copySize(window.frameGeometry);
        });
    }
    return records[key];
}

function resizeAndCenter(window, before, record) {
    var area = workspace.clientArea(0, window.output, workspace.currentDesktop);
    if (!(area.width > 0 && area.height > 0)) return;
    var target = floatingGeometry(before, record.size, area, window.minSize, window.maxSize);
    var job = {
        window: window,
        timer: new QTimer(),
        adjusting: false,
        corrections: 0,
        sizeAttempts: 1
    };
    record.job = job;
    job.cancel = function () { cancelCorrection(record); };
    job.centerActualSize = function () {
        if (record.job !== job || job.adjusting) return;
        if (window.deleted || window.keepBelow || window.fullScreen || window.maximizeMode) {
            cancelCorrection(record);
            return;
        }
        var actual = window.frameGeometry;
        // Wayland may still expose the old tile until the client acknowledges
        // the requested resize. Do not center that obsolete, oversized frame.
        if (actual.width === before.width && actual.height === before.height
            && (target.width !== before.width || target.height !== before.height)) return;
        // An older Wayland configure (Krohnkite's original floating size) can
        // arrive after our resize. Reassert the compact request a bounded number
        // of times, rather than adopting and centering that obsolete large size.
        if ((actual.width > target.width + 16 || actual.height > target.height + 16)
            && job.sizeAttempts < 4) {
            ++job.sizeAttempts;
            job.adjusting = true;
            window.frameGeometry = target;
            job.adjusting = false;
            return;
        }
        var x = Math.round(area.x + (area.width - actual.width) / 2);
        var y = Math.round(area.y + (area.height - actual.height) / 2);
        record.size = copySize(actual);
        if (Math.abs(actual.x - x) <= 1 && Math.abs(actual.y - y) <= 1) return;
        if (++job.corrections > 4) {
            cancelCorrection(record);
            return;
        }
        job.adjusting = true;
        window.frameGeometry = { x: x, y: y, width: actual.width, height: actual.height };
        job.adjusting = false;
    };
    job.timer.singleShot = true;
    job.timer.timeout.connect(job.cancel);
    window.frameGeometryChanged.connect(job.centerActualSize);
    window.interactiveMoveResizeStarted.connect(job.cancel);
    job.timer.start(1000); // Bounded resize acknowledgement, not a background watcher.
    window.frameGeometry = target;
    job.centerActualSize();
}

function toggleCenteredFloat() {
    var window = workspace.activeWindow;
    if (requestInFlight || !window || window.deleted || !window.normalWindow
        || !window.moveable || !window.resizeable || window.fullScreen
        || window.minimized || window.move || window.resize) return;
    var before = copySize(window.frameGeometry);
    var record = recordFor(window);
    cancelCorrection(record);
    // Native maximize is separate from Krohnkite's tiling state.
    if (window.maximizeMode) window.setMaximize(false, false);
    var wasTiled = window.keepBelow;
    if (!wasTiled) record.size = copySize(window.frameGeometry);
    requestInFlight = true;
    var serial = ++requestSerial;
    var request = { timer: new QTimer() };
    pendingRequest = request;
    request.cancel = function () {
        request.timer.stop();
        try { window.keepBelowChanged.disconnect(request.observe); } catch (error) {}
        if (pendingRequest === request) pendingRequest = null;
    };
    request.timer.singleShot = true;
    request.timer.timeout.connect(function () {
        if (serial !== requestSerial || window.deleted || window.keepBelow === wasTiled) return;
        request.cancel();
        requestTimeout.stop();
        requestInFlight = false;
        if (workspace.activeWindow === window && wasTiled && !window.keepBelow
            && !window.fullScreen && !window.maximizeMode)
            resizeAndCenter(window, before, record);
    });
    request.observe = function () {
        if (serial === requestSerial && !window.deleted && window.keepBelow !== wasTiled)
            request.timer.start(0); // Let Krohnkite finish its current commit first.
    };
    window.keepBelowChanged.connect(request.observe);
    requestTimeout.start(1500);
    callDBus("org.kde.kglobalaccel", "/component/kwin",
        "org.kde.kglobalaccel.Component", "invokeShortcut", "KrohnkiteToggleFloat",
        function () {
            if (serial !== requestSerial) return;
            // A D-Bus reply only acknowledges dispatch. The layer-change signal
            // confirms that Krohnkite actually processed the requested toggle.
            request.observe();
        });
}

workspace.windowRemoved.connect(function (window) {
    var key = String(window.internalId);
    if (records[key]) {
        cancelCorrection(records[key]);
        delete records[key];
    }
});

registerShortcut("Toggle Centered Float", "Alternar flotante compacta y centrada", "",
                 toggleCenteredFloat);
