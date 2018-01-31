from threading import Thread, Event
from time import sleep
import schedule
import functools

kill_schedule_daemon_event = Event()

#################################################################
#					Scheduling
#################################################################

#catch errors
def catch_exceptions(job_func, cancel_on_failure=False):
    @functools.wraps(job_func)
    def wrapper(*args, **kwargs):
        try:
            return job_func(*args, **kwargs)
        except:
            import traceback
            print(traceback.format_exc())
            if cancel_on_failure:
                return schedule.CancelJob
    return wrapper

#job threader
def schedule_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

#check the schedule
def schedule_daemon(stop_event):
	while not stop_event.is_set():
		schedule.run_pending()
		sleep(1)
	print '            schdule daemon ending for'

#start the scheduler
def spawn_schedule_daemon():
	print 'starting job scheduler'
	daemon = Thread(target = schedule_daemon, name = 'job scheduler', args = (kill_schedule_daemon_event,))
	daemon.setDaemon(True)
	daemon.start()

#kill the scheduler
def kill_schedule_daemon():
	print 'killing scheduler'
	kill_schedule_daemon_event.set()