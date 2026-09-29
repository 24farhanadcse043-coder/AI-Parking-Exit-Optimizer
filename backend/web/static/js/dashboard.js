/* =========================================================
   PARKAI — REAL-TIME DASHBOARD CONTROLLER
========================================================= */

const API_BASE = "";

let dashboardData = {};
let activityItems = [];


/* =========================================================
   API HELPER
========================================================= */

async function fetchJSON(url, options = {}) {

    const response = await fetch(
        API_BASE + url,
        options
    );

    if (!response.ok) {

        throw new Error(
            `HTTP ${response.status}: ${response.statusText}`
        );

    }

    return await response.json();
}


/* =========================================================
   CLOCK
========================================================= */

function updateClock() {

    const clock = document.getElementById(
        "liveClock"
    );

    if (!clock) {
        return;
    }

    const now = new Date();

    clock.textContent =
        now.toLocaleTimeString(
            "en-IN",
            {
                hour12: false
            }
        );
}

setInterval(
    updateClock,
    1000
);

updateClock();

/* =========================================================
   PARKING STATUS
========================================================= */

async function loadParkingStatus() {

    try {

        const data =
            await fetchJSON(
                "/api/parking/status"
            );

        /*
         * Store the database parking data,
         * but do not update the live dashboard
         * counters from this endpoint.
         *
         * The vision system is the live source
         * for the 7 calibrated parking spaces.
         */

        dashboardData.parking =
            data;

    } catch (error) {

        console.error(
            "Parking API error:",
            error
        );

        addActivity(
            "Parking API connection error",
            "Unable to retrieve parking status.",
            "⚠️"
        );
    }
}

/* =========================================================
   UPDATE PARKING DISPLAY
========================================================= */

function updateParkingDisplay(data) {

    if (!data) {
        return;
    }

    const total =
        Number(data.total_spaces || 0);

    const occupied =
        Number(data.occupied_spaces || 0);

    const available =
        Number(data.available_spaces || 0);

    const percentage =
        Number(
            data.occupancy_percentage || 0
        );

    /* -----------------------------------------
       PARKING COUNTERS
    ----------------------------------------- */

    setText(
        "totalSpaces",
        total
    );

    setText(
        "occupiedSpaces",
        occupied
    );

    setText(
        "availableSpaces",
        available
    );

    setText(
        "totalText",
        total
    );

    setText(
        "occupiedText",
        occupied
    );

    setText(
        "availableText",
        available
    );

    setText(
        "occupancyPercentage",
        `${percentage}%`
    );

    setText(
        "utilizationText",
        `${percentage}%`
    );

    /* -----------------------------------------
       OCCUPANCY BAR
    ----------------------------------------- */

    const bar =
        document.getElementById(
            "occupiedBar"
        );

    if (bar) {

        bar.style.width =
            `${Math.min(
                percentage,
                100
            )}%`;
    }

    /* -----------------------------------------
       OCCUPANCY CIRCLE
    ----------------------------------------- */

    updateOccupancyCircle(
        percentage
    );

    /* -----------------------------------------
       PARKING MAP
    ----------------------------------------- */

    updateParkingMap(
        data
    );
}


/* =========================================================
   PARKING MAP UPDATE
========================================================= */

function updateParkingMap(data) {

    if (!data) {
        return;
    }

    const spaces =
        data.spaces ||
        data.parking_spaces ||
        data.space_status ||
        null;

    if (!spaces) {

        console.log(
            "Parking map: no individual space data."
        );

        return;
    }

    Object.entries(
        spaces
    ).forEach(
        ([spaceNumber, occupied]) => {

            const element =
                document.querySelector(
                    `[data-space="${spaceNumber}"]`
                );

            if (!element) {

                console.warn(
                    `Parking space ${spaceNumber} ` +
                    `not found in dashboard.`
                );

                return;
            }

            /* ---------------------------------
               REMOVE OLD STATUS
            --------------------------------- */

            element.classList.remove(
                "available-space",
                "occupied-space"
            );

            /* ---------------------------------
               STATUS TEXT
            --------------------------------- */

            const status =
                element.querySelector(
                    "small"
                );

            /* ---------------------------------
               OCCUPIED
            --------------------------------- */

            if (occupied === true) {

                element.classList.add(
                    "occupied-space"
                );

                if (status) {

                    status.textContent =
                        "CAR";
                }

            }

            /* ---------------------------------
               FREE
            --------------------------------- */

            else {

                element.classList.add(
                    "available-space"
                );

                if (status) {

                    status.textContent =
                        "FREE";
                }
            }
        }
    );

    console.log(
        "✅ Parking map updated:",
        spaces
    );
}


/* =========================================================
   OCCUPANCY CIRCLE
========================================================= */

function updateOccupancyCircle(
    percentage
) {

    const circle =
        document.getElementById(
            "occupancyCircle"
        );

    if (!circle) {
        return;
    }

    const degrees =
        Math.min(
            Math.max(
                Number(percentage) || 0,
                0
            ),
            100
        ) * 3.6;

    circle.style.background =
        `conic-gradient(
            #3b82f6 ${degrees}deg,
            #1e293b ${degrees}deg
        )`;
}

/* =========================================================
   AI RECOMMENDATION
========================================================= */

async function loadRecommendation() {

    try {

        const data =
            await fetchJSON(
                "/api/recommendations/"
            );

        dashboardData.recommendation =
            data;

        updateRecommendationDisplay(
            data
        );

    } catch (error) {

        console.error(
            "Recommendation API error:",
            error
        );

    }
}


/* =========================================================
   UPDATE RECOMMENDATION DISPLAY
========================================================= */

function updateRecommendationDisplay(
    data
) {

    if (!data) {
        return;
    }

    const recommended =
        data.recommended_exit;

    if (!recommended) {

        setText(
            "recommendedExit",
            "NO EXIT"
        );

        setText(
            "recommendationQueue",
            "--"
        );

        setText(
            "recommendationWait",
            "--"
        );

        setText(
            "recommendationDistance",
            "--"
        );

        setText(
            "recommendationCongestion",
            "UNAVAILABLE"
        );

        return;
    }

    setText(
        "recommendedExit",
        recommended.name
    );

    setText(
        "recommendationQueue",
        recommended.queue_length
    );

    setText(
        "recommendationWait",
        `${recommended.waiting_time} min`
    );

    setText(
        "recommendationDistance",
        `${recommended.distance} m`
    );

    const congestion =
        document.getElementById(
            "recommendationCongestion"
        );

    if (congestion) {

        const level =
            recommended.congestion_level ||
            "UNKNOWN";

        congestion.textContent =
            level;

        congestion.className =
            "congestion-badge " +
            getCongestionClass(
                level
            );
    }
}


/* =========================================================
   EXIT DATA
========================================================= */

async function loadExits() {

    const container =
        document.getElementById(
            "exitContainer"
        );

    if (!container) {
        return;
    }

    try {

        const exits =
            await fetchJSON(
                "/api/exits/"
            );

        dashboardData.exits =
            exits;

        if (!exits.length) {

            container.innerHTML = `
                <div class="loading-card">
                    No parking exits available.
                </div>
            `;

            return;
        }

        container.innerHTML =
            exits.map(
                exit =>
                    createExitCard(
                        exit
                    )
            ).join("");

    } catch (error) {

        console.error(
            "Exit API error:",
            error
        );

        container.innerHTML = `
            <div class="loading-card">
                Unable to connect to exit system.
            </div>
        `;
    }
}


/* =========================================================
   EXIT CARD
========================================================= */

function createExitCard(
    exit
) {

    const congestion =
        String(
            exit.congestion_level ||
            "LOW"
        ).toUpperCase();

    let percentage = 20;

    if (congestion === "MEDIUM") {
        percentage = 55;
    }

    if (congestion === "HIGH") {
        percentage = 90;
    }

    const status =
        exit.is_available
            ? "AVAILABLE"
            : "BLOCKED";

    const statusClass =
        exit.is_available
            ? "available"
            : "unavailable";

    const congestionClass =
        getCongestionClass(
            congestion
        );

    return `

        <div class="exit-card">

            <div
                style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                "
            >

                <h3>
                    🚪 ${escapeHTML(
                        exit.name
                    )}
                </h3>

                <span
                    class="${statusClass}"
                    style="
                        font-size:7px;
                        font-weight:800;
                        letter-spacing:1px;
                    "
                >
                    ● ${status}
                </span>

            </div>

            <div class="exit-data">

                <div>
                    <span>
                        QUEUE
                    </span>

                    <strong>
                        ${exit.queue_length}
                    </strong>
                </div>

                <div>
                    <span>
                        WAITING
                    </span>

                    <strong>
                        ${exit.waiting_time} min
                    </strong>
                </div>

                <div>
                    <span>
                        DISTANCE
                    </span>

                    <strong>
                        ${exit.distance} m
                    </strong>
                </div>

                <div>
                    <span>
                        CONGESTION
                    </span>

                    <strong
                        class="${congestionClass}"
                    >
                        ${congestion}
                    </strong>
                </div>

            </div>

            <div
                class="exit-congestion ${congestionClass}"
            >

                <span
                    style="
                        width:${percentage}%;
                    "
                ></span>

            </div>

            <div
                class="exit-state ${statusClass}"
                style="margin-top:9px;"
            >
                ${status}
            </div>

        </div>

    `;
}


/* =========================================================
   VEHICLES
========================================================= */

async function loadVehicles() {

    const table =
        document.getElementById(
            "vehicleTable"
        );

    if (!table) {
        return;
    }

    try {

        const vehicles =
            await fetchJSON(
                "/api/vehicles/"
            );

        dashboardData.vehicles =
            vehicles;

        const activeVehicles =
            vehicles.filter(
                vehicle =>
                    vehicle.status ===
                    "PARKED" ||
                    vehicle.status ===
                    "ENTERED"
            ).length;

        setText(
            "vehicleCount",
            activeVehicles
        );

        if (!vehicles.length) {

            table.innerHTML = `
                <tr>
                    <td
                        colspan="6"
                        class="loading"
                    >
                        No vehicles registered.
                    </td>
                </tr>
            `;

            return;
        }

        table.innerHTML =
            vehicles.map(
                vehicle =>
                    createVehicleRow(
                        vehicle
                    )
            ).join("");

    } catch (error) {

        console.error(
            "Vehicle API error:",
            error
        );

        table.innerHTML = `
            <tr>
                <td
                    colspan="6"
                    class="loading"
                >
                    Unable to load vehicles.
                </td>
            </tr>
        `;
    }
}


/* =========================================================
   VEHICLE ROW
========================================================= */

function createVehicleRow(
    vehicle
) {

    const status =
        vehicle.status || "UNKNOWN";

    const vehicleNumber =
        String(
            vehicle.vehicle_number || "-"
        ).trim();

    return `

        <tr>

            <td>
                #${vehicle.id}
            </td>

            <td>

                <strong
                    style="color:#f8fafc;"
                >
                    🚗
                    ${escapeHTML(
                        vehicleNumber
                    )}
                </strong>

            </td>

            <td>
                ${escapeHTML(
                    vehicle.parking_space ||
                    "-"
                )}
            </td>

            <td>
                ${escapeHTML(
                    vehicle.current_location ||
                    "-"
                )}
            </td>

            <td>

                <span
                    class="status-badge"
                >
                    ${escapeHTML(
                        status
                    )}
                </span>

            </td>

            <td>

                ${
                    vehicleNumber !== "-"
                        ? `
                            <button
                                class="small-action"
                                onclick="showVehicleRoute('${escapeJS(
                                    vehicleNumber
                                )}')"
                            >
                                ROUTE
                            </button>
                        `
                        : "-"
                }

            </td>

        </tr>

    `;
}


/* =========================================================
   VEHICLE ROUTE
========================================================= */

async function showVehicleRoute(
    vehicleNumber
) {

    try {

        const route =
            await fetchJSON(
                `/api/routes/${encodeURIComponent(
                    vehicleNumber
                )}`
            );

        addActivity(
            `Route calculated for ${vehicleNumber}`,
            `${route.recommended_exit} • ${route.distance} m • ${route.estimated_waiting_time} min`,
            "🗺️"
        );

        alert(
            `AI Route\n\n` +
            `Vehicle: ${vehicleNumber}\n` +
            `Recommended Exit: ${route.recommended_exit}\n` +
            `Distance: ${route.distance} m\n` +
            `Waiting Time: ${route.estimated_waiting_time} min\n` +
            `Congestion: ${route.congestion}`
        );

    } catch (error) {

        console.error(
            "Vehicle route error:",
            error
        );

        alert(
            "Unable to calculate vehicle route."
        );
    }
}


/* =========================================================
   EMERGENCY CONTROLS
========================================================= */

async function loadEmergencyControls() {

    const container =
        document.getElementById(
            "emergencyContainer"
        );

    if (!container) {
        return;
    }

    try {

        const exits =
            await fetchJSON(
                "/api/exits/"
            );

        container.innerHTML =
            exits.map(
                exit =>
                    createEmergencyCard(
                        exit
                    )
            ).join("");

    } catch (error) {

        console.error(
            "Emergency API error:",
            error
        );
    }
}


/* =========================================================
   EMERGENCY CARD
========================================================= */

function createEmergencyCard(
    exit
) {

    const available =
        exit.is_available;

    const button =
        available
            ? `
                <button
                    class="emergency-button"
                    onclick="blockExit(
                        ${exit.id}
                    )"
                >
                    🚨 BLOCK EXIT
                </button>
            `
            : `
                <button
                    class="emergency-button clear-button"
                    onclick="clearExit(
                        ${exit.id}
                    )"
                >
                    ✓ CLEAR EMERGENCY
                </button>
            `;

    return `

        <div class="emergency-card">

            <h3>
                🚪 ${escapeHTML(
                    exit.name
                )}
            </h3>

            <p>
                Current status:

                <strong
                    class="${
                        available
                            ? "available"
                            : "unavailable"
                    }"
                >
                    ${
                        available
                            ? "AVAILABLE"
                            : "BLOCKED"
                    }
                </strong>
            </p>

            ${button}

        </div>

    `;
}


/* =========================================================
   BLOCK EXIT
========================================================= */

async function blockExit(
    exitId
) {

    const confirmed =
        confirm(
            "Block this parking exit?\n\n" +
            "The AI routing system will automatically " +
            "avoid this exit."
        );

    if (!confirmed) {
        return;
    }

    try {

        await fetchJSON(
            `/api/exits/${exitId}/emergency` +
            `?reason=Emergency%20from%20AI%20dashboard`,
            {
                method: "PUT"
            }
        );

        addActivity(
            `Exit ${exitId} blocked`,
            "AI routing automatically updated.",
            "🚨"
        );

        await loadDashboard();

    } catch (error) {

        console.error(
            "Block exit error:",
            error
        );

        alert(
            "Unable to block exit."
        );
    }
}


/* =========================================================
   CLEAR EXIT
========================================================= */

async function clearExit(
    exitId
) {

    try {

        await fetchJSON(
            `/api/exits/${exitId}/clear-emergency`,
            {
                method: "PUT"
            }
        );

        addActivity(
            `Exit ${exitId} restored`,
            "Exit is available again.",
            "✅"
        );

        await loadDashboard();

    } catch (error) {

        console.error(
            "Clear exit error:",
            error
        );

        alert(
            "Unable to clear emergency."
        );
    }
}


/* =========================================================
   VISION DATA
========================================================= */

function updateVisionData(
    data
) {

    if (!data) {
        return;
    }

    const vehicleCount =
        data.active_vehicles ??
        data.vehicle_count ??
        data.total ??
        0;

    setText(
        "detectedVehicles",
        vehicleCount
    );

    setText(
        "visionVehicleCount",
        vehicleCount
    );

    const types =
        data.vehicle_types ||
        data.counts ||
        {};

    setText(
        "carCount",
        types.car || 0
    );

    setText(
        "motorcycleCount",
        types.motorcycle || 0
    );

    setText(
        "busCount",
        types.bus || 0
    );

    setText(
        "truckCount",
        types.truck || 0
    );
}


/* =========================================================
   LIVE VISION API
========================================================= */

async function loadVisionStatus() {

    try {

        const data =
            await fetchJSON(
                "/api/vision/status"
            );

        dashboardData.vision =
            data;

        console.log(
            "Vision status:",
            data
        );

        /* -----------------------------------------
           OVERALL VISION STATUS
        ----------------------------------------- */

        const visionStatus =
            document.getElementById(
                "visionStatus"
            );

        const visionRunning =
            Boolean(
                data.vision_ai &&
                data.vision_ai.running
            );

        if (visionStatus) {

            if (
                data.status === "ACTIVE" &&
                visionRunning
            ) {

                visionStatus.textContent =
                    "AI ACTIVE";

                visionStatus.classList.add(
                    "online"
                );

            } else {

                visionStatus.textContent =
                    "AI OFFLINE";

                visionStatus.classList.remove(
                    "online"
                );
            }
        }

        /* -----------------------------------------
           PARKING VISION
        ----------------------------------------- */

        if (data.parking_vision) {

            const occupancy =
                data.parking_vision.occupancy;

            if (occupancy) {

                updateParkingDisplay(
                    occupancy
                );
            }

            /* -------------------------------------
               VEHICLE TRACKING
            ------------------------------------- */

            const tracking =
                data.parking_vision.vehicle_tracking;

            if (tracking) {

                updateVisionData(
                    tracking
                );

                setText(
                    "activeVehicles",
                    tracking.active_vehicles
                );

                setText(
                    "detectedVehicles",
                    tracking.active_vehicles
                );

                setText(
                    "visionVehicleCount",
                    tracking.active_vehicles
                );
            }
        }

        /* -----------------------------------------
           LIVE AI ANALYSIS
        ----------------------------------------- */

        if (
            data.vision_ai &&
            data.vision_ai.latest_analysis
        ) {

            const latest =
                data.vision_ai.latest_analysis;

            /* -------------------------------------
               AI recommendation
            ------------------------------------- */

            if (latest.recommendation) {

                updateRecommendationDisplay(
                    latest.recommendation
                );
            }

            /* -------------------------------------
               Exit analysis
            ------------------------------------- */

            if (
                latest.analysis &&
                latest.analysis.exits
            ) {

                updateVisionExitAnalysis(
                    latest.analysis.exits
                );
            }

            /* -------------------------------------
               Detected vehicles
            ------------------------------------- */

            if (
                latest.analysis &&
                latest.analysis.vehicles
            ) {

                const vehicles =
                    latest.analysis.vehicles;

                setText(
                    "detectedVehicles",
                    vehicles.length
                );

                setText(
                    "visionVehicleCount",
                    vehicles.length
                );
            }
        }

    } catch (error) {

        console.error(
            "Vision status API error:",
            error
        );

        const visionStatus =
            document.getElementById(
                "visionStatus"
            );

        if (visionStatus) {

            visionStatus.textContent =
                "AI OFFLINE";

            visionStatus.classList.remove(
                "online"
            );
        }
    }
}


/* =========================================================
   LIVE VISION EXIT ANALYSIS
========================================================= */

function updateVisionExitAnalysis(
    exits
) {

    if (!exits) {
        return;
    }

    Object.entries(
        exits
    ).forEach(
        ([exitName, data]) => {

            console.log(
                `Vision ${exitName}:`,
                data
            );

        }
    );
}


/* =========================================================
   DASHBOARD API
========================================================= */

async function loadDashboardOverview() {

    try {

        const data =
            await fetchJSON(
                "/api/dashboard/overview"
            );

        dashboardData.overview =
            data;

        if (data.vehicles) {

            const parked =
                data.vehicles.parked || 0;

            setText(
                "vehicleCount",
                parked
            );
        }

    } catch (error) {

        console.error(
            "Dashboard overview error:",
            error
        );
    }
}


/* =========================================================
   WEBSOCKET — PARKING
========================================================= */

function connectParkingWebSocket() {

    const protocol =
        location.protocol === "https:"
            ? "wss"
            : "ws";

    const socket =
        new WebSocket(
            `${protocol}://${location.host}/ws/parking`
        );

    socket.onopen = () => {

        console.log(
            "🟢 Parking WebSocket connected"
        );

        addActivity(
            "Parking WebSocket connected",
            "Live parking updates enabled.",
            "📡"
        );
    };

    socket.onmessage = event => {

        try {

            const message =
                JSON.parse(
                    event.data
                );

            console.log(
                "Parking WebSocket:",
                message
            );

            if (
                message.type ===
                "PARKING_UPDATE"
            ) {

                if (message.data) {

                    dashboardData.parking =
                        message.data;

                    updateParkingFromWebSocket(
                        message.data
                    );
                }
            }

            if (
                message.type ===
                "PARKING_VISION_UPDATE"
            ) {

                if (message.data) {

                    const data =
                        message.data;

                    if (data.occupancy) {

                        updateParkingFromWebSocket(
                            data.occupancy
                        );
                    }

                    if (
                        data.vehicle_tracking
                    ) {

                        updateVisionData(
                            data.vehicle_tracking
                        );
                    }
                }
            }

            if (
                message.type ===
                "DASHBOARD_UPDATE"
            ) {

                if (message.data) {

                    handleDashboardWebSocket(
                        message.data
                    );
                }
            }

        } catch (error) {

            console.error(
                "Parking WebSocket parse error:",
                error
            );
        }
    };

    socket.onclose = () => {

        console.log(
            "🔴 Parking WebSocket disconnected"
        );

        setTimeout(
            connectParkingWebSocket,
            3000
        );
    };

    socket.onerror = error => {

        console.error(
            "Parking WebSocket error:",
            error
        );
    };
}


/* =========================================================
   PARKING WEBSOCKET UPDATE
========================================================= */

function updateParkingFromWebSocket(
    data
) {

    if (!data) {
        return;
    }

    updateParkingDisplay(
        data
    );
}


/* =========================================================
   DASHBOARD WEBSOCKET
========================================================= */

function handleDashboardWebSocket(
    data
) {

    console.log(
        "Dashboard live update:",
        data
    );

    if (data.parking) {

        updateParkingFromWebSocket(
            data.parking
        );
    }

    if (data.vehicle_tracking) {

        updateVisionData(
            data.vehicle_tracking
        );
    }

    if (data.vehicles) {

        setText(
            "vehicleCount",
            data.vehicles.parked || 0
        );
    }

    if (data.vision) {

        dashboardData.vision =
            data.vision;
    }

    addActivity(
        "Dashboard synchronized",
        "Real-time backend data received.",
        "📡"
    );
}


/* =========================================================
   WEBSOCKET — RECOMMENDATIONS
========================================================= */

function connectRecommendationWebSocket() {

    const protocol =
        location.protocol === "https:"
            ? "wss"
            : "ws";

    const socket =
        new WebSocket(
            `${protocol}://${location.host}/ws/recommendations`
        );

    socket.onopen = () => {

        console.log(
            "🟢 Recommendation WebSocket connected"
        );
    };

    socket.onmessage = event => {

        try {

            const message =
                JSON.parse(
                    event.data
                );

            if (
                message.type ===
                "AI_EXIT_RECOMMENDATION"
            ) {

                updateRecommendationFromWebSocket(
                    message.data
                );
            }

        } catch (error) {

            console.error(
                "Recommendation WebSocket error:",
                error
            );
        }
    };

    socket.onclose = () => {

        setTimeout(
            connectRecommendationWebSocket,
            3000
        );
    };

    socket.onerror = error => {

        console.error(
            "Recommendation WebSocket error:",
            error
        );
    };
}


/* =========================================================
   RECOMMENDATION WEBSOCKET UPDATE
========================================================= */

function updateRecommendationFromWebSocket(
    data
) {

    if (!data) {
        return;
    }

    dashboardData.recommendation =
        data;

    updateRecommendationDisplay(
        data
    );

    const recommended =
        data.recommended_exit;

    if (!recommended) {
        return;
    }

    addActivity(
        `AI route changed to ${recommended.name}`,
        `Congestion: ${recommended.congestion_level}`,
        "🧠"
    );
}


/* =========================================================
   DASHBOARD VISION WEBSOCKET
========================================================= */

function connectDashboardWebSocket() {

    const protocol =
        location.protocol === "https:"
            ? "wss"
            : "ws";

    const socket =
        new WebSocket(
            `${protocol}://${location.host}/ws/dashboard`
        );

    socket.onopen = () => {

        console.log(
            "🟢 Dashboard WebSocket connected"
        );

        addActivity(
            "Dashboard WebSocket connected",
            "Live dashboard synchronization enabled.",
            "📡"
        );
    };

    socket.onmessage = event => {

        try {

            const message =
                JSON.parse(
                    event.data
                );

            console.log(
                "Dashboard WebSocket:",
                message
            );

            if (
                message.type ===
                "DASHBOARD_UPDATE"
            ) {

                handleDashboardWebSocket(
                    message.data
                );
            }

            if (
                message.type ===
                "VISION_EXIT_UPDATE"
            ) {

                if (message.data) {

                    if (
                        message.data.analysis
                    ) {

                        const analysis =
                            message.data.analysis;

                        if (
                            analysis.exits
                        ) {

                            updateVisionExitAnalysis(
                                analysis.exits
                            );
                        }
                    }

                    if (
                        message.data.recommendation
                    ) {

                        updateRecommendationDisplay(
                            message.data.recommendation
                        );
                    }
                }
            }

        } catch (error) {

            console.error(
                "Dashboard WebSocket parse error:",
                error
            );
        }
    };

    socket.onclose = () => {

        console.log(
            "🔴 Dashboard WebSocket disconnected"
        );

        setTimeout(
            connectDashboardWebSocket,
            3000
        );
    };

    socket.onerror = error => {

        console.error(
            "Dashboard WebSocket error:",
            error
        );
    };
}


/* =========================================================
   GENERAL DASHBOARD LOAD
========================================================= */

async function loadDashboard() {

    await Promise.all([
        loadParkingStatus(),
        loadRecommendation(),
        loadExits(),
        loadVehicles(),
        loadEmergencyControls(),
        loadDashboardOverview(),
        loadVisionStatus(),
        loadCameraStatus()
    ]);

}


/* =========================================================
   ACTIVITY FEED
========================================================= */

function addActivity(
    title,
    description,
    icon = "●"
) {

    const feed =
        document.getElementById(
            "activityFeed"
        );

    if (!feed) {
        return;
    }

    const time =
        new Date().toLocaleTimeString(
            "en-IN",
            {
                hour12: false
            }
        );

    const item = {
        title,
        description,
        icon,
        time
    };

    activityItems.unshift(
        item
    );

    activityItems =
        activityItems.slice(
            0,
            8
        );

    feed.innerHTML =
        activityItems.map(
            activity => `

                <div class="activity-item">

                    <span class="activity-icon blue">
                        ${activity.icon}
                    </span>

                    <div>

                        <strong>
                            ${escapeHTML(
                                activity.title
                            )}
                        </strong>

                        <small>
                            ${escapeHTML(
                                activity.description
                            )}
                        </small>

                    </div>

                    <time>
                        ${activity.time}
                    </time>

                </div>

            `
        ).join("");
}


/* =========================================================
   UTILITY FUNCTIONS
========================================================= */

function setText(
    elementId,
    value
) {

    const element =
        document.getElementById(
            elementId
        );

    if (element) {

        element.textContent =
            value;
    }
}


function getCongestionClass(
    level
) {

    const normalized =
        String(
            level || ""
        ).toLowerCase();

    if (
        normalized === "low"
    ) {

        return "low";

    }

    if (
        normalized === "medium"
    ) {

        return "medium";

    }

    if (
        normalized === "high"
    ) {

        return "high";

    }

    return "";
}


function escapeHTML(
    value
) {

    return String(
        value ?? ""
    )
        .replaceAll(
            "&",
            "&amp;"
        )
        .replaceAll(
            "<",
            "&lt;"
        )
        .replaceAll(
            ">",
            "&gt;"
        )
        .replaceAll(
            '"',
            "&quot;"
        )
        .replaceAll(
            "'",
            "&#039;"
        );
}


function escapeJS(
    value
) {

    return String(
        value ?? ""
    )
        .replaceAll(
            "\\",
            "\\\\"
        )
        .replaceAll(
            "'",
            "\\'"
        )
        .replaceAll(
            "\n",
            "\\n"
        );
}


/* =========================================================
   START DASHBOARD
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        console.log(
            "🚀 ParkAI dashboard starting..."
        );

        initializeCameraStream();

        loadCameraStatus();

        loadDashboard();

        connectParkingWebSocket();

        connectRecommendationWebSocket();

        connectDashboardWebSocket();

        /*
         * REST API is used as a safety fallback.
         * WebSockets provide the real-time updates.
         */

        setInterval(
            loadDashboard,
            10000
        );

    }
);


/* =========================================================
   LIVE CAMERA STREAM
========================================================= */

function initializeCameraStream() {

    const camera =
        document.getElementById(
            "liveCameraStream"
        );

    const offlineMessage =
        document.getElementById(
            "cameraOfflineMessage"
        );

    const cameraStatus =
        document.getElementById(
            "cameraAIStatus"
        );


    if (!camera) {

        console.warn(
            "⚠️ Live camera element not found."
        );

        return;
    }


    /* -----------------------------------------------------
       CAMERA STREAM CONNECTED
    ----------------------------------------------------- */

    camera.onload = function () {

        console.log(
            "🟢 Live camera stream connected."
        );


        if (offlineMessage) {

            offlineMessage.style.display =
                "none";
        }


        if (cameraStatus) {

            cameraStatus.textContent =
                "AI TRACKING";

            cameraStatus.classList.add(
                "online"
            );
        }

    };


    /* -----------------------------------------------------
       CAMERA STREAM ERROR
    ----------------------------------------------------- */

    camera.onerror = function () {

        console.error(
            "🔴 Live camera stream unavailable."
        );


        if (offlineMessage) {

            offlineMessage.style.display =
                "flex";
        }


        if (cameraStatus) {

            cameraStatus.textContent =
                "CAMERA OFFLINE";

            cameraStatus.classList.remove(
                "online"
            );
        }

    };

}


/* =========================================================
   CAMERA STATUS API
========================================================= */

async function loadCameraStatus() {

    try {

        const data =
            await fetchJSON(
                "/api/vision/camera/status"
            );


        const camera =
            document.getElementById(
                "liveCameraStream"
            );

        const offlineMessage =
            document.getElementById(
                "cameraOfflineMessage"
            );

        const cameraStatus =
            document.getElementById(
                "cameraAIStatus"
            );


        if (
            data.camera === "ONLINE" &&
            data.running === true &&
            data.frame_available === true
        ) {

            console.log(
                "🟢 Camera API: ONLINE"
            );


            if (offlineMessage) {

                offlineMessage.style.display =
                    "none";
            }


            if (cameraStatus) {

                cameraStatus.textContent =
                    "AI TRACKING";
            }


            /*
             * If the image element lost the stream,
             * reload it.
             */

            if (
                camera &&
                !camera.src
            ) {

                camera.src =
                    "/api/vision/camera/stream";
            }

        } else {

            console.warn(
                "🔴 Camera API: OFFLINE"
            );


            if (offlineMessage) {

                offlineMessage.style.display =
                    "flex";
            }


            if (cameraStatus) {

                cameraStatus.textContent =
                    "CAMERA OFFLINE";
            }

        }

    } catch (error) {

        console.error(
            "Camera status error:",
            error
        );


        const offlineMessage =
            document.getElementById(
                "cameraOfflineMessage"
            );


        if (offlineMessage) {

            offlineMessage.style.display =
                "flex";
        }

    }

}