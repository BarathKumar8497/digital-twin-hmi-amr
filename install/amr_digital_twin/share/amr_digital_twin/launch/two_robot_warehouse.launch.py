#!/usr/bin/env python3
"""
Launch file: spawns two TurtleBot3 (burger) robots into the AWS small warehouse
world, each in its own ROS 2 namespace (tb1, tb2) so they can be controlled
and monitored independently.

Usage:
    ros2 launch amr_digital_twin two_robot_warehouse.launch.py
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    # --- Paths ---
    turtlebot3_gazebo_dir = get_package_share_directory('turtlebot3_gazebo')

    # Path to your warehouse world file (edit this if your username/path differs)
    warehouse_world = os.path.expanduser(
        '~/warehouse_ws/src/aws-robomaker-small-warehouse-world/'
        'worlds/small_warehouse/small_warehouse.world'
    )

    # TurtleBot3 burger URDF/SDF model file (installed with turtlebot3_gazebo)
    model_folder = 'turtlebot3_burger'
    sdf_path = os.path.join(
        turtlebot3_gazebo_dir, 'models', model_folder, 'model.sdf'
    )

    # --- 1. Start Gazebo with the warehouse world ---
    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', '-r', warehouse_world],
        output='screen'
    )

    # --- 2. Spawn Robot 1 (tb1) near the LEFT shelf row ---
    spawn_tb1 = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'tb1',
            '-file', sdf_path,
            '-x', '-3.0', '-y', '2.0', '-z', '0.05',
            '-Y', '0.0'
        ],
        output='screen'
    )

    # --- 3. Spawn Robot 2 (tb2) near the RIGHT shelf row ---
    spawn_tb2 = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'tb2',
            '-file', sdf_path,
            '-x', '3.0', '-y', '2.0', '-z', '0.05',
            '-Y', '3.14'
        ],
        output='screen'
    )

    # --- 4. Bridge tb1 topics (Gazebo <-> ROS 2), under /tb1 namespace ---
    bridge_tb1 = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        namespace='tb1',
        arguments=[
            '/model/tb1/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/model/tb1/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry',
        ],
        remappings=[
            ('/model/tb1/cmd_vel', '/tb1/cmd_vel'),
            ('/model/tb1/odometry', '/tb1/odom'),
        ],
        output='screen'
    )

    # --- 5. Bridge tb2 topics, under /tb2 namespace ---
    bridge_tb2 = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        namespace='tb2',
        arguments=[
            '/model/tb2/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/model/tb2/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry',
        ],
        remappings=[
            ('/model/tb2/cmd_vel', '/tb2/cmd_vel'),
            ('/model/tb2/odometry', '/tb2/odom'),
        ],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        spawn_tb1,
        spawn_tb2,
        bridge_tb1,
        bridge_tb2,
    ])
