from collections import defaultdict

import threading

class EventController: 
    def __init__(self, events_handled_per_tick=10, queue_overflow_limit=100):
        self.__event_queue_lock = threading.Lock()
        self.__event_queue = []
        self.__listeners = defaultdict(list)
        self.__events_handled_per_tick = events_handled_per_tick
        self.__queue_overflow_limit = queue_overflow_limit

    def handle_events(self, *args):
        events_handled = 0
        for i in range(0, min(self.__events_handled_per_tick, len(self.__event_queue))):
            event = self.__event_queue[i]
            for listener in self.__listeners[event.getType()]:
                listener(event)
            events_handled += 1
            print("Handled Event: " + str(event))
        self.__event_queue_lock.acquire()
        self.__event_queue = self.__event_queue[events_handled:]
        self.__event_queue_lock.release()

        if(len(self.__event_queue) > self.__queue_overflow_limit):
            print("Warning: Event queue has overflowed. Current queue size is: " + str(len(self.__event_queue)) + "... Dropping Events...")
            self.__event_queue_lock.acquire()
            self.__event_queue = self.__event_queue[:-self.__queue_overflow_limit]
            self.__event_queue_lock.release()

    def sendEvent(self, event):
        self.__event_queue_lock.acquire()
        self.__event_queue.append(event)
        self.__event_queue_lock.release()
        
    def addEventListener(self, eventType, eventListernFunction):
        self.__listeners[eventType].append(eventListernFunction)

class Event:
    def __init__(self, eventType, source, details=None):
        self.__eventType = eventType
        self.__source = source
        self.__details = details
    def getDetails(self):
        return self.__details
    def getType(self):
        return self.__eventType
    def getSource(self):
        return self.__source
    def __str__(self):
        return "Event(" + str(self.__source) + " -> " + str(self.__eventType) + "|{" + str(self.__details) + "})"