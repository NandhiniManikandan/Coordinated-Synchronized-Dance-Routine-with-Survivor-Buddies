import json
import time

from Event import Event

class Timeline:
	TEMPORAL_WAYPOINTS = "temporal_waypoints"
	WAYPOINT_TIME_SEC = "time_sec"
	WAYPOINT_NAME = "name"
	WAYPOINT_ARGS = "args"
	def __init__(self, timeline_path):
		self.__start_time = None
		f = open(timeline_path, "r")
		self.__timeline_data = json.load(f)
		f.close()
		self.__init_fired_events()
	
	def __waypoint_key(self, waypoint):
		return str(waypoint[self.WAYPOINT_NAME]) + "-" + str(waypoint[self.WAYPOINT_TIME_SEC])

	def __fired(self, waypoint):
		return self.__fired_events[self.__waypoint_key(waypoint)]

	def __fire(self, waypoint):
		self.__fired_events[self.__waypoint_key(waypoint)] = True

	def __init_fired_events(self):
		self.__fired_events = {self.__waypoint_key(wp):False for wp in self.__timeline_data[self.TEMPORAL_WAYPOINTS]}

	def done(self):
		for _, value in self.__fired_events.items():
			if(value == False):
				return False
		return True

	def start(self):
		self.__init_fired_events()
		self.__start_time = time.time()
		return True

	def tick(self, event_controller):
		if(self.__start_time is None):
			raise Exception("Attempting to call tick on a timeline that has not been started yet. Please call .start() before ticking the timeline.")
		current_time = time.time()
		tick_time = current_time-self.__start_time

		for waypoint in self.__timeline_data[self.TEMPORAL_WAYPOINTS]:
			if(not self.__fired(waypoint) and waypoint[self.WAYPOINT_TIME_SEC] < tick_time):
				self.__fire(waypoint)
				e = Event(waypoint[self.WAYPOINT_NAME], "TIMELINE", waypoint[self.WAYPOINT_ARGS])
				event_controller.sendEvent(e)




