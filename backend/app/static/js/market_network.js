document.addEventListener("DOMContentLoaded", function () {

    const simulateButton = document.getElementById("simulateButton");
    const shockInstrument = document.getElementById("shockInstrument");
    const shockValue = document.getElementById("shockValue");
    const simulationResults = document.getElementById("simulationResults");

    /*
        DEMO MODEL

        Bunlar şimdilik örnek sensitivity katsayılarıdır.

        Örneğin:
        Brent %1 yükseldiğinde DXY'nin yaklaşık %0.071
        yükseldiğini varsayıyoruz.

        SONRA:
        Bu sabit değerleri kaldıracağız.
        Tarihsel piyasa verisinden hesaplayacağız.
    */

    const models = {

        oil: {
            "DXY": 0.071,
            "Gold": -0.159,
            "Silver": -0.122,
            "S&P 500": -0.131,
            "Nasdaq 100": -0.216,
            "BIST 100": -0.093,
            "USD/TRY": 0.184
        },

        gold: {
            "DXY": -0.31,
            "Gold": 1,
            "Silver": 0.72,
            "S&P 500": 0.08,
            "Nasdaq 100": 0.05,
            "BIST 100": 0.14,
            "USD/TRY": 0.18
        },

        dxy: {
            "DXY": 1,
            "Gold": -0.62,
            "Silver": -0.55,
            "S&P 500": -0.28,
            "Nasdaq 100": -0.35,
            "BIST 100": -0.42,
            "USD/TRY": 0.48
        },

        rates: {
            "DXY": 0.32,
            "Gold": -0.51,
            "Silver": -0.44,
            "S&P 500": -0.35,
            "Nasdaq 100": -0.57,
            "BIST 100": -0.22,
            "USD/TRY": 0.16
        },

        nasdaq: {
            "DXY": -0.10,
            "Gold": 0.08,
            "Silver": 0.15,
            "S&P 500": 0.78,
            "Nasdaq 100": 1,
            "BIST 100": 0.32,
            "USD/TRY": -0.12
        }

    };


    simulateButton.addEventListener("click", function () {

        const instrument = shockInstrument.value;
        const shock = parseFloat(shockValue.value);

        if (isNaN(shock)) {
            alert("Please enter a valid shock value.");
            return;
        }

        const model = models[instrument];

        if (!model) {
            alert("Simulation model not found.");
            return;
        }

        simulationResults.innerHTML = "";

        Object.entries(model).forEach(function ([name, coefficient]) {

            const result = shock * coefficient;

            const row = document.createElement("div");
            row.className = "result-row";

            const instrumentName = document.createElement("span");
            instrumentName.textContent = name;

            const value = document.createElement("strong");

            if (result > 0) {

                value.className = "positive";
                value.textContent = "+" + result.toFixed(2) + "% ↑";

            } else if (result < 0) {

                value.className = "negative";
                value.textContent = result.toFixed(2) + "% ↓";

            } else {

                value.textContent = "0.00%";

            }

            row.appendChild(instrumentName);
            row.appendChild(value);

            simulationResults.appendChild(row);

        });

    });

});