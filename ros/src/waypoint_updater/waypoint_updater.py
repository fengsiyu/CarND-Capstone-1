#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped
from styx_msgs.msg import Lane, Waypoint

import math

'''
This node will publish waypoints from the car's current position to some `x` distance ahead.

As mentioned in the doc, you should ideally first implement a version which does not care
about traffic lights or obstacles.

Once you have created dbw_node, you will update this node to use the status of traffic lights too.

Please note that our simulator also provides the exact location of traffic lights and their
current status in `/vehicle/traffic_lights` message. You can use this message to build this node
as well as to verify your TL classifier.

TODO (for Yousuf and Aaron): Stopline location for each traffic light.
'''

LOOKAHEAD_WPS = 200 # Number of waypoints we will publish. You can change this number


class WaypointUpdater(object):
    def __init__(self):
        rospy.init_node('waypoint_updater')

        rospy.Subscriber('/current_pose', PoseStamped, self.pose_cb)
        rospy.Subscriber('/base_waypoints', Lane, self.waypoints_cb)

        # TODO: Add a subscriber for /traffic_waypoint and /obstacle_waypoint below


        self.final_waypoints_pub = rospy.Publisher('final_waypoints', Lane, queue_size=1)

        # TODO: Add other member variables you need below
        self.current_pose = None
        self.waypoints = None
        self.next_wp_idx = 0

        rospy.spin()

    def pose_cb(self, msg):
        # TODO: Done Implement
        rospy.loginfo('current_pose Received - x:%d, y:%d,z:%d', msg.pose.position.x,msg.pose.position.y,
                      msg.pose.position.z)
        self.current_pose = msg
        if self.waypoints!= None:
            #get next waypoints
            last_wp_idx = self.next_wp_idx -1
            dl = lambda a, b: math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)
            distance_cp_to_last_wp = dl(self.waypoints[last_wp_idx].pose.pose.position,
                                        self.current_pose.pose.position)

            next_wp_idx = self.next_wp_idx
            while self.distance(self.waypoints,last_wp_idx,next_wp_idx)< distance_cp_to_last_wp:
                next_wp_idx +=1

            #rospy.loginfo('next_wp_index:%d', self.next_wp_idx)
            if next_wp_idx > self.next_wp_idx:
                self.next_wp_idx = next_wp_idx
                # publish new final waypoints
                lane = Lane()
                lane.header.frame_id = '/world'
                lane.header.stamp = rospy.Time(0)
                lane.waypoints = self.waypoints[self.next_wp_idx:(self.next_wp_idx+LOOKAHEAD_WPS)]
                self.final_waypoints_pub.publish(lane)
                rospy.loginfo('publish final waypoint - next_wp_index:%d', self.next_wp_idx)

    def waypoints_cb(self, waypoints):
        # TODO: Done Implement
        #rospy.loginfo('waypoints Received - count:%d',len(waypoints.waypoints))
        self.waypoints = waypoints.waypoints

    def traffic_cb(self, msg):
        # TODO: Callback for /traffic_waypoint message. Implement
        pass

    def obstacle_cb(self, msg):
        # TODO: Callback for /obstacle_waypoint message. We will implement it later
        pass

    def get_waypoint_velocity(self, waypoint):
        return waypoint.twist.twist.linear.x

    def set_waypoint_velocity(self, waypoints, waypoint, velocity):
        waypoints[waypoint].twist.twist.linear.x = velocity

    def distance(self, waypoints, wp1, wp2):
        dist = 0
        dl = lambda a, b: math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2  + (a.z-b.z)**2)
        for i in range(wp1, wp2+1):
            dist += dl(waypoints[wp1].pose.pose.position, waypoints[i].pose.pose.position)
            wp1 = i
        return dist


if __name__ == '__main__':
    try:
        WaypointUpdater()
    except rospy.ROSInterruptException:
        rospy.logerr('Could not start waypoint updater node.')
