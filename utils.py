import datetime
import time

def datetime_to_timestamp(target_date : str, target_time : str) -> int:
    date = [x for x in target_date.split('.')] 
    date += [x for x in target_time.split(':')]

    newdate = datetime.datetime(*map(int, date))

    return newdate.timestamp()

def timestamp_to_date(timestamp : int) -> str:
    return str(datetime.datetime.fromtimestamp(timestamp))

def get_current_timestamp() -> int:
    return int(time.time())


