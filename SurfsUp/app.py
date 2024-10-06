# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
Base.classes.keys()

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

"""Start at the homepage.
List all the available routes."""

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate App Homepage<br/>"
        f"Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"/api/v1.0/start<br/>"
        f"(enter as YYYY-MM-DD)<br/><br/>"
        f"/api/v1.0/start/end<br/>"
        f"(enter as YYYY-MM-DD/YYYY-MM-DD)"
    )

#################################################

"""Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data)
 to a dictionary using date as the key and prcp as the value."""
"""Return the JSON representation of your dictionary"""

@app.route("/api/v1.0/precipitation")
def precipitation():
    recent_date = session.query(func.Max(Measurement.date)).scalar()
    result = []
    x = recent_date.split('-')
    for i in x:
        if i.isnumeric():
            result.append(int(i))
    year_past = dt.date(result[0], result[1], result[2]) - dt.timedelta(days=365)
    data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_past).\
        order_by(Measurement.date).all()
    
    precipitation_dict = dict(data)
    
    return jsonify(precipitation_dict)
#################################################

"""Return a JSON list of stations from the dataset."""

@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(Station.name, Station.station, Station.latitude, Station.longitude, Station.elevation)
    station_list = []
    for name,station,lat,lon,elev in stations_query:
        station = {}
        station["Name"] = name
        station["Station"] = station
        station["Latitude"] = lat
        station["Longitude"] = lon
        station["Elevation"] = elev
        station_list.append(station)

    return jsonify(stations)

#################################################

"""Query the dates and temperature observations of the most-active station for the previous year of data."""
"""Return a JSON list of temperature observations for the previous year."""

@app.route("/api/v1.0/tobs")
def tobs():
    recent_date = session.query(func.Max(Measurement.date)).scalar()
    result = []
    x = recent_date.split('-')
    for i in x:
        if i.isnumeric():
            result.append(int(i))
    year_past = dt.date(result[0], result[1], result[2]) - dt.timedelta(days=365)
    temp = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_past).\
        filter(Measurement.station=='USC00519281').\
        order_by(Measurement.date).all()
    
    temp_total = []
    for d,t in temp:
        temperature = {}
        temperature["Date"] = d
        temperature["Temperature"] = t
        temp_total.append(temperature)

        return jsonify(temp_total)
#################################################

"""Return a JSON list of the minimum temperature, the average temperature,
 and the maximum temperature for a specified start or start-end range."""
"""For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date."""
"""For a specified start date and end date, calculate TMIN, TAVG, and TMAX
 for the dates from the start date to the end date, inclusive."""

@app.route("/api/v1.0/<start>")
def start_temp(start_input):
    start = dt.datetime.strptime(start_input, '%Y-%m-%d')
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    temp_list = []
    for min, avg, max in temp_data:
        temp_dict = {}
        temp_dict['TMIN'] = min
        temp_dict['TAVG'] = avg
        temp_dict['TMAX'] = max
        temp_list.append(temp_dict)

    return jsonify(temp_list)

#################################################

"""Return a JSON list of the minimum temperature, the average temperature,
 and the maximum temperature for a specified start or start-end range."""
"""For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date."""
"""For a specified start date and end date, calculate TMIN, TAVG, and TMAX
 for the dates from the start date to the end date, inclusive."""

@app.route("/api/v1.0/<start>/<end>")
def start_end_temp(start_input, end_input):
    start = dt.datetime.strptime(start_input, '%Y-%m-%d')
    end = dt.datetime.strptime(end_input, '%Y-%m-%d')
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    temp_list = []
    for min, avg, max in temp_data:
        temp_dict = {}
        temp_dict['TMIN'] = min
        temp_dict['TAVG'] = avg
        temp_dict['TMAX'] = max
        temp_list.append(temp_dict)

    return jsonify(temp_list)
#################################################

if __name__ == '__main__':
    app.run(debug=True)