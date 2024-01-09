
from Timeline import Timeline
from Event import EventController

ec = EventController()
tl = Timeline("timelines/thriller.json")

def sample_act_on_waypoint(event, robot_id=None):
    print(str(robot_id) + " <- Event:" + str(event))

#"concern" is the name of an event in the thriller.json file
#The function sample_act_on_waypoint will be fired every time that event is fired
#commands to each robot can be wrapped inside one of these functions
ec.addEventListener("concern", sample_act_on_waypoint)

#You can add the same multiple times too, here "dance_1_thriller" is another entry in thriller.json
ec.addEventListener("dance_1_thriller", lambda x: sample_act_on_waypoint(x, "sample_robot_id_0"))
ec.addEventListener("dance_1_thriller", lambda x: sample_act_on_waypoint(x, "sample_robot_id_1"))
ec.addEventListener("dance_1_thriller", lambda x: sample_act_on_waypoint(x, "sample_robot_id_2"))
ec.addEventListener("dance_1_thriller", lambda x: sample_act_on_waypoint(x, "sample_robot_id_3"))

tl.start()
while(not tl.done()):
    tl.tick(ec)
    ec.handle_events()