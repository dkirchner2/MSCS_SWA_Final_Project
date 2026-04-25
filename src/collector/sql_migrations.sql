DROP TABLE IF EXISTS Locations;
DROP TABLE IF EXISTS WeatherEntries;

CREATE TABLE Locations (
    locationID INTEGER PRIMARY KEY NOT NULL,
    cityName VARCHAR(255) NOT NULL,
    stateName VARCHAR(255),
    stateAbbr VARCHAR(255),
    latitude REAL,
    longitude REAL
);

CREATE TABLE WeatherEntries (
    entryID INTEGER PRIMARY KEY AUTOINCREMENT,
    locationID INTEGER REFERENCES Locations(locationID),
    entryDate VARCHAR(255),
    maxTemp REAL,
    minTemp REAL,
    daylightDuration REAL,
    sunlightDuration REAL,
    rainInches REAL,
    snowInches REAL,
    precipitationHours REAL,
    windGusts REAL,
    averageTemp REAL,
    cloudCover REAL,
    averageWindSpeed REAL,
    averageHumidity REAL,
    created TIMESTAMP
);