import json, datetime
def datetime_to_timestamp():
    get_timestamp = datetime.datetime.now().timestamp()
    return str(int(get_timestamp))

def get_current_time():
    get_time = datetime.datetime.now()
    return get_time

if __name__ == '__main__':
    print(datetime_to_timestamp())


