from threading import Lock

stats_data = {}
stats_lock = Lock() #allows only one function at a time
