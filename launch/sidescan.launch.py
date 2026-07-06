from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg_share = get_package_share_directory('sidescan_ros2')
    default_config = os.path.join(pkg_share, 'config', 'omniscan450_params.yaml')
    sensor_number = LaunchConfiguration('sensor_number')

    return LaunchDescription([
        DeclareLaunchArgument('sensor_number', default_value='450'),
        DeclareLaunchArgument('port_ip_address', default_value='192.168.2.93'),
        DeclareLaunchArgument('port_port', default_value='51200'),
        DeclareLaunchArgument('starboard_ip_address', default_value='192.168.2.95'),
        DeclareLaunchArgument('starboard_port', default_value='51200'),
        DeclareLaunchArgument('config_file', default_value=default_config),
        Node(
            package='sidescan_ros2',
            executable='sidescan_node',
            name=PythonExpression(["'omniscan' + '", sensor_number, "'"]),
            output='screen',
            respawn=True,
            respawn_delay=30.0,
            parameters=[
                LaunchConfiguration('config_file'),
                {
                    'sensor_number': sensor_number,
                    'port_ip_address': LaunchConfiguration('port_ip_address'),
                    'port_port': PythonExpression(["int('", LaunchConfiguration('port_port'), "')"]),
                    'starboard_ip_address': LaunchConfiguration('starboard_ip_address'),
                    'starboard_port': PythonExpression(
                        ["int('", LaunchConfiguration('starboard_port'), "')"]),
                },
            ],
        ),
    ])
