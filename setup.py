from setuptools import setup

package_name = 'sidescan_ros2'
node_package = 'sidescan_ros2_nodes'

setup(
    name=package_name,
    version='0.1.0',
    packages=[node_package, 'brping'],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Monika Roznere',
    maintainer_email='mrozner1@binghamton.edu',
    description='ROS2 driver for Cerulean Omniscan 450 side scan sonar',
    license='MIT',
    entry_points={
        'console_scripts': [
            'sidescan_node = sidescan_ros2_nodes.sidescan_node:main',
            'sidescan_all_node = sidescan_ros2_nodes.sidescan_all_node:main',
        ],
    },
)
