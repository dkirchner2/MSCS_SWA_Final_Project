let selectedLocations = ['', '', '', '', ''];
let locations_arr = [];

document.getElementById('city1').addEventListener('input', (event) => {
    searchDropdown(1, event.target.value);
});

document.getElementById('city2').addEventListener('input', (event) => {
    searchDropdown(2, event.target.value);
});

document.getElementById('city3').addEventListener('input', (event) => {
    searchDropdown(3, event.target.value);
});

document.getElementById('city4').addEventListener('input', (event) => {
    searchDropdown(4, event.target.value);
});

document.getElementById('city5').addEventListener('input', (event) => {
    searchDropdown(5, event.target.value);
});

document.getElementById('submit-button').addEventListener('click', (event) => {
    getCityData();
})

function initLocations(locations) {
    locations_arr = locations
}

function searchDropdown(input_box_num, search_text) {
    let list_element = document.getElementById(`list${input_box_num}`);
    list_element.innerHTML = '';
    document.getElementById('results').style.display = 'none';
    document.getElementById('submit-button').disabled = true;
    selectedLocations[input_box_num - 1] = '';
    if (search_text === '') {
        return;
    }
    let results = locations_arr.filter(loc => loc['cityName'].toLowerCase().includes(search_text.toLowerCase())
        || loc['stateName'].toLowerCase().includes(search_text.toLowerCase())).slice(0, 5);
    if (results.length === 0) {
        const li = document.createElement("li");
        li.textContent = "No results found";
        list_element.appendChild(li);
    } else {
        results.forEach(res => {
            const li = document.createElement("li");
            li.textContent = `${res['cityName']}, ${res['stateName']}`;
            li.onclick = function () {
                onSearchResultClick(input_box_num, res);
            };
            list_element.appendChild(li);
        });
    }
}

function onSearchResultClick(input_box_num, location) {
    console.log('clicked')
    console.log(location);
    document.getElementById(`city${input_box_num}`).value = `${location['cityName']}, ${location['stateName']}`;
    let list_element = document.getElementById(`list${input_box_num}`);
    list_element.innerHTML = '';
    selectedLocations[input_box_num - 1] = location;
    console.log(selectedLocations);
    if (input_box_num < 5) {
        document.getElementById(`city${input_box_num + 1}`).disabled = false;
    }
    document.getElementById('submit-button').disabled = false;
}

function getCityData() {
    idx_list = [];
    for (loc of selectedLocations) {
        if (loc !== '') {
            idx_list.push(loc['locationID']);
        }
    }

    fetch('/cities', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 'cities': idx_list })
    })
        .then(response => response.json())
        .then(data => fillCityTable(data))
        .catch(error => console.error('Error:', error));
}

function fillCityTable(data) {
    console.log(data);
    document.getElementById('results').style.display = 'block';
    const mean_table_rows = document.querySelector("#mean-results-table tbody");
    if (mean_table_rows) {
        mean_table_rows.innerHTML = "";
    }

    const max_table_rows = document.querySelector("#max-results-table tbody");
    if (max_table_rows) {
        max_table_rows.innerHTML = "";
    }

    const min_table_rows = document.querySelector("#min-results-table tbody");
    if (min_table_rows) {
        min_table_rows.innerHTML = "";
    }

    for (let i = 0; i < data.length; i++) {
        let newRow = mean_table_rows.insertRow(-1);
        newRow.style.backgroundColor = 'darkmagenta';
        newRow.insertCell(0).textContent = `${selectedLocations[i]['cityName']}, ${selectedLocations[i]['stateName']}`;
        for (let i = 1; i < 13; i++) {
            newRow.insertCell(i);
        }
        addTableRow(mean_table_rows, data[i], 'combined_monthly_means', 'maxTemp', 'Max Daily Temperature (F)');
        addTableRow(mean_table_rows, data[i], 'combined_monthly_means', 'averageTemp', 'Mean Daily Temperature (F)');
        addTableRow(mean_table_rows, data[i], 'combined_monthly_means', 'minTemp', 'Min Daily Temperature (F)');
        addTableRow(mean_table_rows, data[i], 'combined_monthly_means', 'averageHumidity', 'Average Daily Humidity');
        addTableRow(mean_table_rows, data[i], 'combined_monthly_means', 'rainInchesMonthly', 'Average Monthly Rainfall (in)');
        addTableRow(mean_table_rows, data[i], 'combined_monthly_means', 'snowInchesMonthly', 'Average Montly Snowfall (in)');
        addTableRow(mean_table_rows, data[i], 'combined_monthly_means', 'precipitationHours', 'Average Precipitation Duration (hrs)');
        addTableRow(mean_table_rows, data[i], 'combined_monthly_means', 'daylightDuration', 'Average Daylight Duration (hrs)');
        addTableRow(mean_table_rows, data[i], 'combined_monthly_means', 'sunlightDuration', 'Average Sunlight Duration (hrs)');
        addTableRow(mean_table_rows, data[i], 'combined_monthly_means', 'cloudCover', 'Average Daily Cloud Cover');
        addTableRow(mean_table_rows, data[i], 'combined_monthly_means', 'averageWindSpeed', 'Average Daily Wind Speed (mph)');
        addTableRow(mean_table_rows, data[i], 'combined_monthly_means', 'windGusts', 'Average Max Wind Gusts (mph)');

        newRow = max_table_rows.insertRow(-1);
        newRow.style.backgroundColor = 'darkmagenta';
        newRow.insertCell(0).textContent = `${selectedLocations[i]['cityName']}, ${selectedLocations[i]['stateName']}`;
        for (let i = 1; i < 13; i++) {
            newRow.insertCell(i);
        }
        addTableRow(max_table_rows, data[i], 'combined_monthly_maxes', 'maxTemp', 'Max Daily Temperature (F)');
        addTableRow(max_table_rows, data[i], 'combined_monthly_maxes', 'averageTemp', 'Mean Daily Temperature (F)');
        addTableRow(max_table_rows, data[i], 'combined_monthly_maxes', 'minTemp', 'Min Daily Temperature (F)');
        addTableRow(max_table_rows, data[i], 'combined_monthly_maxes', 'averageHumidity', 'Average Daily Humidity');
        addTableRow(max_table_rows, data[i], 'combined_monthly_maxes', 'rainInchesMonthly', 'Average Monthly Rainfall (in)');
        addTableRow(max_table_rows, data[i], 'combined_monthly_maxes', 'snowInchesMonthly', 'Average Monthly Snowfall (in)');
        addTableRow(max_table_rows, data[i], 'combined_monthly_maxes', 'precipitationHours', 'Average Precipitation Duration (hrs)');
        addTableRow(max_table_rows, data[i], 'combined_monthly_maxes', 'daylightDuration', 'Average Daylight Duration (hrs)');
        addTableRow(max_table_rows, data[i], 'combined_monthly_maxes', 'sunlightDuration', 'Average Sunlight Duration (hrs)');
        addTableRow(max_table_rows, data[i], 'combined_monthly_maxes', 'cloudCover', 'Average Daily Cloud Cover');
        addTableRow(max_table_rows, data[i], 'combined_monthly_maxes', 'averageWindSpeed', 'Average Daily Wind Speed (mph)');
        addTableRow(max_table_rows, data[i], 'combined_monthly_maxes', 'windGusts', 'Average Max Wind Gusts (mph)');

        newRow = min_table_rows.insertRow(-1);
        newRow.style.backgroundColor = 'darkmagenta';
        newRow.insertCell(0).textContent = `${selectedLocations[i]['cityName']}, ${selectedLocations[i]['stateName']}`;
        for (let i = 1; i < 13; i++) {
            newRow.insertCell(i);
        }
        addTableRow(min_table_rows, data[i], 'combined_monthly_mins', 'maxTemp', 'Max Daily Temperature (F)');
        addTableRow(min_table_rows, data[i], 'combined_monthly_mins', 'averageTemp', 'Mean Daily Temperature (F)');
        addTableRow(min_table_rows, data[i], 'combined_monthly_mins', 'minTemp', 'Min Daily Temperature (F)');
        addTableRow(min_table_rows, data[i], 'combined_monthly_mins', 'averageHumidity', 'Average Daily Humidity');
        addTableRow(min_table_rows, data[i], 'combined_monthly_mins', 'rainInchesMonthly', 'Average Monthly Rainfall (in)');
        addTableRow(min_table_rows, data[i], 'combined_monthly_mins', 'snowInchesMonthly', 'Average Monthly Snowfall (in)');
        addTableRow(min_table_rows, data[i], 'combined_monthly_mins', 'precipitationHours', 'Average Precipitation Duration (hrs)');
        addTableRow(min_table_rows, data[i], 'combined_monthly_mins', 'daylightDuration', 'Average Daylight Duration (hrs)');
        addTableRow(min_table_rows, data[i], 'combined_monthly_mins', 'sunlightDuration', 'Average Sunlight Duration (hrs)');
        addTableRow(min_table_rows, data[i], 'combined_monthly_mins', 'cloudCover', 'Average Daily Cloud Cover');
        addTableRow(min_table_rows, data[i], 'combined_monthly_mins', 'averageWindSpeed', 'Average Daily Wind Speed (mph)');
        addTableRow(min_table_rows, data[i], 'combined_monthly_mins', 'windGusts', 'Average Max Wind Gusts (mph)');

    }
}

function addTableRow(table, cityData, stat, substat, heading) {
    const months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'];
    let newRow = table.insertRow(-1);
    newRow.insertCell(0).textContent = heading;
    for (let i = 0; i < months.length; i++) {
        newRow.insertCell(i + 1).textContent = Math.round(cityData[stat][substat][months[i]]);
    }
}