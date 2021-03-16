import datetime
import time

def datetime_to_timestamp(target_date : str, target_time : str) -> int:
    date = [x for x in target_date.split('.')] 
    date += [x for x in target_time.split(':')]

    newdate = datetime.datetime(*map(int, date))

    return newdate.timestamp()