#!/usr/bin/env python3

# Python imports
import numpy as np
import rospy
import time

from geometry_msgs.msg import TwistStamped
from std_msgs.msg import String 
from Timeline import Timeline
from Event import EventController

class SBCoordinator(object):
    """
    Dance corrdinator class
    """
    def __init__(self):
        self.twist = TwistStamped()

        self.publishers = [rospy.Publisher(f"/sb_{i}_cmd_state", TwistStamped, queue_size=10) for i in range(4)]
        self.cmd_publishers = [rospy.Publisher(f"/sb_{i}_cmd", String, queue_size=4) for i in range(4)]
        self.cmd_subscribers = [rospy.Subscriber(f"/sb_{i}_cmd", String, callback=self.sb_callback, queue_size=4, callback_args=i) for i in range(4)]
        self.rate = rospy.Rate(10)

        self.current_state = np.zeros((4,4)) # Each row corresponds to the joint state of a robot
        self.robot_active = [False,False,False,False] # Is a robot currently in motion?

        print("Wait for it...")
        time.sleep(1) # For some reason, it takes a bit for everything to get up and running, so we must wait for a bit after initialization.
        self.reset_all()


    def sb_callback(self, msg, robot_id):

        """
        This method processes the action designated by the script and sends it to the corresponding robot. 
        Additional actions can be added by including additional elif statements with the appropriate angles.
        """

        data = msg.data.split()
        cmd = data[0]
        if cmd != "reset":
            angle = float(data[1])
        delay = float(data[2])

        cs = self.current_state[robot_id,:]

        if cmd == "lean":
            goal_state = np.array([angle, cs[1], cs[2], cs[3]])
        
        elif cmd == "turn":
            goal_state = np.array([cs[0], angle, cs[2], cs[3]])

        elif cmd == "twist":
            goal_state = np.array([cs[0], cs[1], angle, cs[3]])

        elif cmd == "tilt":
            goal_state = np.array([cs[0], cs[1], cs[2], angle])

        elif cmd == "lean_and_twist":
            goal_state = np.array([angle, cs[1], angle, cs[3]])

        elif cmd == "lean_and_tilt":
            goal_state = np.array([angle, cs[1], cs[2], -angle])

        elif cmd == "turn_and_twist":
            goal_state = np.array([cs[0], angle, -angle, cs[3]])

        elif cmd == "turn_and_tilt":
            goal_state = np.array([cs[0], angle, cs[2], angle])
        
        elif cmd == "tilt_in_place":
            goal_state = np.array([cs[0], cs[1], cs[2], angle])

        elif cmd == "reset":
            goal_state = np.array([0.0, 0.0, 0.0, 0.0])
        
        if cmd != "reset":
            print(f"Robot {robot_id} "+cmd+" "+str(angle)+" deg")
        if delay != 0.0:
            self.delay_motion(robot_id,goal_state,delay)
        else:
            self.move_robot(robot_id,goal_state)

        self.rate.sleep()

    def reset_all(self):
        """
        Resets the orientation of all robots. Typically called at the beginning of the routine.
        """

        goal_state = np.array([0.0, 0.0, 0.0, 0.0])
        print("Resetting robots")
        for robot_id in range(4):
            self.move_robot(robot_id,goal_state)

    def run(self, txt_script):
        """
        This method runs the designated routine found at the txt_script file location.
        """

        with open(txt_script) as f: # Read routine file
            lines = f.readlines()
        print([line.replace("\n", "") for line in lines])
        print("Script received. Let's do this.")
        cmd_value_pairs = [line.replace("\n", "").split() for line in lines]
        for pair in cmd_value_pairs:
            if pair[0] != "wait":
                self.cmd_publishers[int(pair[1])].publish(pair[0]+" "+pair[2]+" "+pair[3])
            else:
                time.sleep(float(pair[1]))
        while any(robot == True for robot in self.robot_active):
            pass # Wait for all robots to finish moving before continuing

    def move_robot(self, robot_id, goal_state):
        """
        Move a robot's joints to a desired goal state.
        """

        self.twist.twist.linear.x  = goal_state[0]
        self.twist.twist.linear.y  = goal_state[1]
        self.twist.twist.linear.z  = goal_state[2]
        self.twist.twist.angular.x = goal_state[3]

        self.publishers[robot_id].publish(self.twist)
        self.current_state[robot_id,:] = goal_state

    def delay_motion(self, robot_id, final_state, delay):
        """
        For more complex movements, specify the time (in seconds) it takes to execute a motion.
        """
        
        steps = int(delay*10)
        initial_state = self.current_state[robot_id,:]
        omega = (final_state - initial_state) / steps
        self.robot_active[robot_id] = True
        for i in range(steps):
            goal_state = self.current_state[robot_id,:] + omega
            self.move_robot(robot_id,goal_state)
            rospy.sleep(delay/steps)
        self.robot_active[robot_id] = False

if __name__ == '__main__':
    rospy.init_node("Lab_4_node", anonymous=True)
    rospy.loginfo("Lab 4 Node started.")
    coord = SBCoordinator()
    # rospy.spin() # Commented out to allow functions below to execute

    ec = EventController()
    tl = Timeline("timelines/thriller.json")

    def run_script(event):
        print("Event:" + str(event))
        print("\tFiring Script: " + str(event.getDetails()["script_path"]))
        coord.run(event.getDetails()["script_path"])

    ec.addEventListener("intro", run_script)
    ec.addEventListener("walk_in", run_script)
    ec.addEventListener("concern", run_script)
    ec.addEventListener("dance_1_thriller", run_script)
    ec.addEventListener("dance_2_line", run_script)
    ec.addEventListener("dance_3_hinge", run_script)
    ec.addEventListener("face_turns", run_script)
    ec.addEventListener("dance_4_turns", run_script)
    ec.addEventListener("thriller_chorus", run_script)
    ec.addEventListener("thriller_chorus", run_script)
    ec.addEventListener("run_away", run_script)
    ec.addEventListener("wake_up", run_script)
    ec.addEventListener("end", run_script)

    tl.start()
    while (not tl.done()) and (not rospy.is_shutdown()):
        tl.tick(ec)
        ec.handle_events()