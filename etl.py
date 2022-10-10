import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format, dayofweek
from pyspark.sql.types import TimestampType



config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID']=config['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY']=config['AWS_SECRET_ACCESS_KEY']


def create_spark_session():
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
    """ 
        Processes song data and creates songs and artists' tables
    
        Input Param:
            spark: SparkSession object
            input_data: S3 endpoint input path
            output_data: S3 endpoint output path
    """
    # get filepath to song data file
    song_data = os.path.join(input_data + 'song_data/*/*/*/*.json')
    
    # read song data file
    df = spark.read.json(song_data).dropDuplicates(subset=['song_id'])

    # extract columns to create songs table
    songs_table = df.select('song_id', 'title', 'artist_id', 'year', 'duration').distinct()
    
    # write songs table to parquet files partitioned by year and artist
    songs_table.write.mode("overwrite").partitionBy('year', 'artist_id').parquet(path=output_data + 'songs')

    # extract columns to create artists table
    artists_table = df.select('artist_id', 'artist_name', 'artist_location', 'artist_latitude', 'artist_longitude').distinct()
    
    # write artists table to parquet files
    artists_table.write.mode("overwrite").parquet(path=output_data + 'artists')
    
    # create a view of song data
    df.createOrReplaceTempView("song_view")


def process_log_data(spark, input_data, output_data):
    """ 
        Processes log data and creates songs and artists' tables
    
        Input Param:
            spark: SparkSession object
            input_data: S3 endpoint input path
            output_data: S3 endpoint output path
    """
    # get filepath to log data file
    log_data = os.path.join(input_data + 'log_data/*/*/*.json')

    # read log data file
    df = spark.read.json(log_data).dropDuplicates(subset=['userId'])
    
    # filter by actions for song plays
    df = df.where(df['page'] == 'NextSong')

    # extract columns for users table    
    artists_table = df.select('userId', 'firstName', 'lastName', 'gender', 'level').distinct()
    
    # write users table to parquet files
    artists_table.write.mode("overwrite").parquet(path=output_data + 'users')

    # create timestamp column from original timestamp column
    get_timestamp = udf(lambda x: datetime.fromtimestamp(x / 1000), TimestampType())
    df = df.withColumn("timestamp", get_timestamp(col("ts")))
    
    # create datetime column from original timestamp column
    get_datetime = udf(lambda x: to_date(x), TimestampType())
    df = df.withColumn("start_time", get_timestamp(col("ts")))
    
    # extract columns to create time table
    df = df.withColumn("hour", hour("timestamp"))
    df = df.withColumn("day", dayofmonth("timestamp"))
    df = df.withColumn("month", month("timestamp"))
    df = df.withColumn("year", year("timestamp"))
    df = df.withColumn("week", weekofyear("timestamp"))
    df = df.withColumn("weekday", dayofweek("timestamp"))

    time_table = df.select('start_time', 'hour', 'day', 'week', 'month', 'year', 'weekday').distinct()
    
    
    # write time table to parquet files partitioned bay year and month
    time_table.write.mode('overwrite').partitionBy('year', 'month').parquet(path=output_data + 'time')

    # read in song data to use for songplays table
    song_df = spark.sql("SELECT * FROM song_view")

    # extract columns from joined song and log datasets to create songplays table 
    songplays_table = df.join(song_df, (df.song == song_df.title) & (df.artist == song_df.artist_name) & (df.length == song_df.duration), "inner")\
                        .distinct().select('start_time', 'userId', 'level', 'song_id', 'artist_id', 'sessionId', 'location', 'userAgent')\
                        .withColumn("songplay_id", monotonically_increasing_id())

    # write songplays table to parquet files partitioned by year and month
    songplays_table.write.mode("overwrite").partitionBy('year', 'month')\
                   .parquet(path=output_data + 'songplays')


def main():
    spark = create_spark_session()
    input_data = "s3a://udacity-dend/"
    output_data = "s3://dest_output_bucket/"
    
    process_song_data(spark, input_data, output_data)    
    process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
    main()
