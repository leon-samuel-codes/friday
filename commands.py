from datetime import datetime

def get_time():
    now = datetime.now()
    return now.strftime("%I:%M:%S %p")        # 

def get_date():
    now = datetime.now()
    return now.strftime("%A, %d %B %Y")

