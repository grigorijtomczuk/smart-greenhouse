function getTemperatureData() {
    $.ajax({
        type: "GET",
        url: "/connect/temperature",
        dataType: "json",
        contentType: "application/json",
        data: {},
        success: function (response) {
            document.getElementById("temperature_value").value = response.value + " " + response.unit;
        }
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
            document.getElementById("humidity_value").value = response.value + " " + response.unit;
        }
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
            document.getElementById("soil_value").value = response.value + " " + response.unit;
        }
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
            document.getElementById("fan_power").value = response.power + " Вт; статус: " + response.status;
        }
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
            document.getElementById("pump_power").value = response.power + " Вт; статус: " + response.status;
        }
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
            document.getElementById("controller_mode").value = "Режим: " + response.mode;
            document.getElementById("controller_alerts").value = "Тревоги: " + response.alerts_count;
        }
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
            document.getElementById("db_connection").value = "Соединение: " + response.connection;
            document.getElementById("db_records").value = "Записей за сегодня: " + response.records_today;
        }
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

setInterval(updateDashboard, 1000);
updateDashboard();
