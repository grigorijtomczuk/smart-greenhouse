function getTemperatureData() {
    $.ajax({
        type: "GET",
        url: "/connect/temperature",
        dataType: "json",
        contentType: "application/json",
        data: {},
        success: function (response) {
            $("#temperature_value").val(response.value + " " + response.unit);
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
    $.ajax({
        type: "GET",
        url: "/connect/database",
        dataType: "json",
        contentType: "application/json",
        data: {},
        success: function (response) {
            $("#db_connection").val("Соединение: " + response.connection);
            $("#db_records").val("Записей за сегодня: " + response.records_today);
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
