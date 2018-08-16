#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import rospy
import actionlib
from control_msgs.msg import (FollowJointTrajectoryAction,
                              FollowJointTrajectoryGoal, GripperCommandAction,
                              GripperCommandGoal)
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

arm_joint_names = [
    "shoulder_pan_joint", "shoulder_lift_joint", "upperarm_roll_joint",
    "elbow_flex_joint", "forearm_roll_joint", "wrist_flex_joint",
    "wrist_roll_joint"
]
arm_intermediate_positions = [1.32, 0, -1.4, 1.72, 0.0, 1.66, 0.0]
arm_joint_positions = [1.32, 1.40, -0.2, 1.72, 0.0, 1.66, 0.0]
# arm_joint_positions  = [-0.595508, -0.914319, 1.15083, 1.52896, 0.688713, -0.660242, -1.23424]

head_joint_names = ["head_pan_joint", "head_tilt_joint"]
head_joint_positions = [0.0, 0.0]

if __name__ == "__main__":
    rospy.init_node("prepare_simulated_robot")

    # Check robot serial number, we never want to run this on a real robot!
    if rospy.get_param("robot/serial") != "ABCDEFGHIJKLMNOPQRSTUVWX":
        rospy.logerr("This script should not be run on a real robot")
        sys.exit(-1)

    rospy.loginfo("Waiting for head_controller...")
    head_client = actionlib.SimpleActionClient(
        "head_controller/follow_joint_trajectory", FollowJointTrajectoryAction)
    head_client.wait_for_server()
    rospy.loginfo("...connected.")

    rospy.loginfo("Waiting for arm_controller...")
    arm_client = actionlib.SimpleActionClient(
        "arm_controller/follow_joint_trajectory", FollowJointTrajectoryAction)
    arm_client.wait_for_server()
    rospy.loginfo("...connected.")

    rospy.loginfo("Waiting for gripper_controller...")
    gripper_client = actionlib.SimpleActionClient(
        "gripper_controller/gripper_action", GripperCommandAction)
    gripper_client.wait_for_server()
    rospy.loginfo("...connected.")

    trajectory = JointTrajectory()
    trajectory.joint_names = head_joint_names
    trajectory.points.append(JointTrajectoryPoint())
    trajectory.points[0].positions = head_joint_positions
    trajectory.points[0].velocities = [0.0] * len(head_joint_positions)
    trajectory.points[0].accelerations = [0.0] * len(head_joint_positions)
    trajectory.points[0].time_from_start = rospy.Duration(5.0)

    head_goal = FollowJointTrajectoryGoal()
    head_goal.trajectory = trajectory
    head_goal.goal_time_tolerance = rospy.Duration(0.0)

    trajectory = JointTrajectory()
    trajectory.joint_names = arm_joint_names
    trajectory.points.append(JointTrajectoryPoint())
    trajectory.points[0].positions = [0.0] * len(arm_joint_positions)
    trajectory.points[0].velocities = [0.0] * len(arm_joint_positions)
    trajectory.points[0].accelerations = [0.0] * len(arm_joint_positions)
    trajectory.points[0].time_from_start = rospy.Duration(1.0)
    trajectory.points.append(JointTrajectoryPoint())
    trajectory.points[1].positions = arm_intermediate_positions
    trajectory.points[1].velocities = [0.0] * len(arm_joint_positions)
    trajectory.points[1].accelerations = [0.0] * len(arm_joint_positions)
    trajectory.points[1].time_from_start = rospy.Duration(4.0)
    trajectory.points.append(JointTrajectoryPoint())
    trajectory.points[2].positions = arm_joint_positions
    trajectory.points[2].velocities = [0.0] * len(arm_joint_positions)
    trajectory.points[2].accelerations = [0.0] * len(arm_joint_positions)
    trajectory.points[2].time_from_start = rospy.Duration(7.5)

    arm_goal = FollowJointTrajectoryGoal()
    arm_goal.trajectory = trajectory
    arm_goal.goal_time_tolerance = rospy.Duration(0.0)

    gripper_goal = GripperCommandGoal()
    gripper_goal.command.max_effort = 10.0
    gripper_goal.command.position = 0.1

    rospy.loginfo("Setting positions...")
    head_client.send_goal(head_goal)
    arm_client.send_goal(arm_goal)
    gripper_client.send_goal(gripper_goal)
    gripper_client.wait_for_result(rospy.Duration(5.0))
    arm_client.wait_for_result(rospy.Duration(6.0))
    head_client.wait_for_result(rospy.Duration(6.0))
    rospy.loginfo("...done")
