# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Welcome/Homepage Route
@app.route("/")
def welcome():
    return(
        f"<h1>Welcome to the Climate App for APIs</h1><br/>"
        f"<h1>Please see below for the available API routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

# Start with defining the calculations that yield the data from the previous year
def prev_year():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Find the most recent date in the data set.
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # Calculate the date one year from the last date in data set.
    start_date = dt.datetime.strptime(recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    # Close the Session
    session.close()
    # Check that the start date was successful
    return(start_date)


@app.route("/api/v1.0/precipitation")
def precipitation():
     # Create our session (link) from Python to the DB
    session = Session(engine) 
    # Perform a query to retrieve the data and precipitation scores
    precip_query = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date > prev_year).\
    order_by(Measurement.date).all()
    # Close the Session
    session.close()
    # Create and append the list of the precipitation data from a dictionary of the data from the last 12 months
    precip_list = []
    for date, prcp in precip_query:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precip_list.append(precip_dict)
    # Return the JSON representation of the dictionary.
    return jsonify(precip_list)

# Set up the Stations Page
@app.route("/api/v1.0/stations")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Perform a query to retrieve the stations
    stations_query = session.query(Station.station).all()
    # Close the Session
    session.close()
    # Make the list of tubles from my stations query into a normal list to be returned in JSON form
    station_list = list(np.ravel(stations_query))
    # Return the JSON representation of my stations list
    return jsonify(station_list)

# Set up the Tobs Page
@app.route("/api/v1.0/tobs")
def tobs(): 
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Perform a query to pull the data from the last year 
    tobs_query = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= prev_year()).all()
    # Close the Session
    session.close()
    # Like with the Precipitation data, create and append a dictionary of the data from the tobs query
    tobs_list = []
    for date, tobs in tobs_query:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)
    # Return the JSON representation of my tobs list
    return jsonify(tobs_list)

# Set up the Start Date or Start-End Range Page
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")

def temps(start=None, end=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Create the list that I want to query
    query_list = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    # Set the if statement for if the end date is present
    if end == None:
        # Perform a query to retrieve the data from the start date to the most recent date
        start_data = session.query(*query_list).\
            filter(Measurement.date >= start).all()
        # Make the list of tubles from my query into a normal list to be returned in JSON form
        start_data_list = list(np.ravel(start_data))
        # Return the JSON representation of minimum, average, and maximum temperatures
        return jsonify(start_data_list)
    else:
        # Perform a query to retrieve the data from the start date to the end date
        end_data = session.query(*query_list).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
        # Make the list of tubles from my query into a normal list to be returned in JSON form
        end_data_list = list(np.ravel((end_data)))
        # Return the JSON representation of minimum, average, and maximum temperatures
        return jsonify(end_data_list)
    # Close the Session
    session.close()

    # Define the main branch
if __name__ == '__main__':
    app.run(debug=True)
