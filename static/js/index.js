let units = {
    temperature: "",
    humidity: "",
    soil_moisture: "",
};

function getTemperatureData() {
    $.ajax({
        type: "GET",
        url: "/connect/temperature",
        dataType: "json",
        contentType: "application/json",
        data: {},
        success: function (response) {
            $("#temperature_value").val(response.value + " " + response.unit);
            units.temperature = response.unit || "";
        },
    });
}

function getHumidityData() {
    $.ajax({
        type: "GET",
        url: "/connect/humidity",
        dataType: "json",
        contentType: "application/json",
        data: {},
        success: function (response) {
            $("#humidity_value").val(response.value + " " + response.unit);
            units.humidity = response.unit || "";
        },
    });
}

function getSoilData() {
    $.ajax({
        type: "GET",
        url: "/connect/soil",
        dataType: "json",
        contentType: "application/json",
        data: {},
        success: function (response) {
            $("#soil_value").val(response.value + " " + response.unit);
            units.soil_moisture = response.unit || "";
        },
    });
}

function getFanData() {
    $.ajax({
        type: "GET",
        url: "/connect/fan",
        dataType: "json",
        contentType: "application/json",
        data: {},
        success: function (response) {
            $("#fan_power").val(
                response.power + " Вт; статус: " + response.status
            );
        },
    });
}

function getPumpData() {
    $.ajax({
        type: "GET",
        url: "/connect/pump",
        dataType: "json",
        contentType: "application/json",
        data: {},
        success: function (response) {
            $("#pump_power").val(
                response.power + " Вт; статус: " + response.status
            );
        },
    });
}

function getControllerData() {
    $.ajax({
        type: "GET",
        url: "/connect/controller",
        dataType: "json",
        contentType: "application/json",
        data: {},
        success: function (response) {
            $("#controller_mode").val("Режим: " + response.mode);
            $("#controller_alerts").val("Тревоги: " + response.alerts_count);
        },
    });
}

function getDatabaseData() {
    function formatValue(number, unit, fractionDigits = 1) {
        if (typeof number !== "number" || Number.isNaN(number)) return "—";
        return number.toFixed(fractionDigits) + " " + (unit || "");
    }

    $.ajax({
        type: "GET",
        url: "/connect/database",
        dataType: "json",
        contentType: "application/json",
        data: {},
        success: function (response) {
            $("#db_connection").val("Соединение: " + response.connection);
            if (response.db_name)
                $("#db_name").val("MongoDB база: " + response.db_name);
            else $("#db_name").val("MongoDB база: —");

            if (typeof response.records_total !== "undefined")
                $("#db_records").val("Записей всего: " + response.records_total);
            else $("#db_records").val("Записей всего: —");

            if (response.collections) {
                const entries = Object.entries(response.collections);
                entries.sort((a, b) => (b[1] || 0) - (a[1] || 0));
                const lines = entries.map(([k, v]) => `${k}: ${v}`);
                $("#db_collections").val(lines.join("\n") || "Коллекций пока нет");
            } else $("#db_collections").val("Коллекций: —");

            const analytics = response.analytics || {};
            const temp = analytics.temperature || {};
            const humidity = analytics.humidity || {};
            const soil_moisture = analytics.soil_moisture || {};

            $("#temperature_avg").val(
                temp.error ? "ошибка" : formatValue(temp.avg, units.temperature)
            );
            $("#temperature_max").val(
                temp.error ? "ошибка" : formatValue(temp.max, units.temperature)
            );

            $("#humidity_avg").val(
                humidity.error ? "ошибка" : formatValue(humidity.avg, units.humidity)
            );
            $("#humidity_max").val(
                humidity.error ? "ошибка" : formatValue(humidity.max, units.humidity)
            );

            $("#soil_avg").val(
                soil_moisture.error
                    ? "ошибка"
                    : formatValue(soil_moisture.avg, units.soil_moisture)
            );
            $("#soil_max").val(
                soil_moisture.error
                    ? "ошибка"
                    : formatValue(soil_moisture.max, units.soil_moisture)
            );
        },
    });
}

function updateDashboard() {
    getTemperatureData();
    getHumidityData();
    getSoilData();
    getFanData();
    getPumpData();
    getControllerData();
    getDatabaseData();
}

function collectCommandPayload() {
    return {
        temperature_power: $("#temperature_power").val(),
        temperature_calibrate: $("#temperature_calibrate").val(),
        humidity_power: $("#humidity_power").val(),
        humidity_calibrate: $("#humidity_calibrate").val(),
        soil_power: $("#soil_power").val(),
        soil_calibrate: $("#soil_calibrate").val(),
        fan_power_cmd: $("#fan_power_cmd").val(),
        fan_power_state: $("#fan_power_state").val(),
        fan_action: $("#fan_action").val(),
        pump_power_cmd: $("#pump_power_cmd").val(),
        pump_power_state: $("#pump_power_state").val(),
        pump_action: $("#pump_action").val(),
        controller_mode: $("#controller_mode_cmd").val(),
        controller_clear_alerts: $("#controller_clear_alerts").is(":checked")
            ? "1"
            : "",
        database_command: $("#database_command").val(),
    };
}

function sendCommands() {
    $.ajax({
        type: "GET",
        url: "/connect/command",
        dataType: "json",
        contentType: "application/json",
        data: collectCommandPayload(),
        success: function (response) {
            $("#command_result").val(JSON.stringify(response, null, 2));
        },
    });
}

$("#send_commands").on("click", sendCommands);

setInterval(updateDashboard, 1000);
updateDashboard();
