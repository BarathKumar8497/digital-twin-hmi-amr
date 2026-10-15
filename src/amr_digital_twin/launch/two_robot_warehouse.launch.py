import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node


def make_sdf(name):
    pkg = get_package_share_directory('turtlebot3_gazebo')
    path = os.path.join(pkg, 'models', 'turtlebot3_burger', 'model.sdf')
    with open(path) as f:
        sdf = f.read()
    # give each robot its own topic names
    sdf = sdf.replace('<topic>cmd_vel</topic>', f'<topic>/model/{name}/cmd_vel</topic>')
    sdf = sdf.replace('<odom_topic>odom</odom_topic>', f'<odom_topic>/model/{name}/odometry</odom_topic>')
    sdf = sdf.replace('<tf_topic>/tf</tf_topic>', f'<tf_topic>/model/{name}/tf</tf_topic>')
    return sdf


def spawn(name, x, y, yaw):
    return Node(
        package='ros_gz_sim', executable='create', output='screen',
        arguments=['-name', name, '-string', make_sdf(name),
                   '-x', str(x), '-y', str(y), '-z', '0.05', '-Y', str(yaw)])


def bridge(name):
    return Node(
        package='ros_gz_bridge', executable='parameter_bridge', namespace=name, output='screen',
        arguments=[f'/model/{name}/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
                   f'/model/{name}/odometry@nav_msgs/msg/Odometry[gz.msgs.Odometry'],
        remappings=[(f'/model/{name}/cmd_vel', f'/{name}/cmd_vel'),
                    (f'/model/{name}/odometry', f'/{name}/odom')])


def generate_launch_description():
    world = os.path.expanduser(
        '~/warehouse_ws/src/aws-robomaker-small-warehouse-world/'
        'worlds/small_warehouse/small_warehouse.world')
    return LaunchDescription([
        ExecuteProcess(cmd=['gz', 'sim', '-r', world], output='screen'),
        spawn('tb1', -3.0, 2.0, 0.0),
        spawn('tb2', 3.0, 2.0, 3.14),
        bridge('tb1'),
        bridge('tb2'),
    ])
