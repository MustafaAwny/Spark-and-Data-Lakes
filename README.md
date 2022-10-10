# Data Lake with Spark

This project is part of Udacity Data Engineer Nanodegree

## Introduction

A music streaming startup, Sparkify, has grown their user base and song database even more and want to move their data warehouse to a data lake. Their data resides in S3, in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

They'd like a data engineer to build an ETL pipeline that extracts their data from S3, processes them using Spark, and loads the data back into S3 as a set of dimensional tables. This will allow their analytics team to continue finding insights in what songs their users are listening to.

## Data

**Song Dataset**: it is in the format of JSON files and each file attributes are: num_songs, artist_id, artist_latitude, artist_longitude, artist_location, artist_name, song_id, title, duration, and year.

**Log Dataset**: it is in the format of JSON files and each file attributes are: artist, auth, firstName, gender, itemInSession, lastName, length, level, location, method, page, registration, sessionId, song, status, ts, userAgent, and userId.

## Project Steps

1- Launch an AWS EMR cluster 

2- Modeling the data tables keeping in mind the queries needed to run

3- Loading the data into tables created in Apache Cassandra and running the queries


## How to run the project

First you need to have Python3, Jupyter Notebook and Apache Cassandra installed on your machine or VM.