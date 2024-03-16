import time

# wraps time output from TimeChecker
class TimeWrapper:
    def __init__(self, t: time) -> None:
        self.t = t
        
    def get_time(self) -> time:
        return self.t
        
    # just prints a difference
    def print_time(self, prefix = "") -> None:
        print(">> time check {} = {} sec.".format(prefix, self.t))

# checks time diffs
class TimeChecker:    
    def __init__(self) -> None:
        self.time_req_begin = time.perf_counter()
        self.last_check_time = self.time_req_begin
    
    # returns time from the begining
    def check_all_time(self) -> TimeWrapper:
        self.last_check_time = time.perf_counter()
        return TimeWrapper(time.time() - self.time_req_begin)
    
    # return a diff beetwen last check and now
    def check_last_time(self) -> TimeWrapper:
        time_diff = time.perf_counter() - self.last_check_time
        self.last_check_time = time.perf_counter()
        return TimeWrapper(time_diff)
    
    