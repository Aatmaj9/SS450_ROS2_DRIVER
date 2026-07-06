#!/usr/bin/env python3

"""
  Author: Monika Roznere
  Affiliation: Binghamton University
  Date: 07/19/2025

  Description:
  Publishes sensor reading from the omniscan sidescan (port, starboard, bow, stern).
"""

import time

import rclpy
from rclpy.node import Node

from sidescan_ros2.msg import SideScanSonarAll, SideScanSonarAllRaw
from sidescan_ros2_nodes.omniscan450_driver import Omniscan450Driver
from sidescan_ros2_nodes.sonar_params import (
    SONAR_PARAM_DEFAULTS,
    declare_sonar_params,
    get_sonar_params,
    make_param_callback,
    timer_period_sec,
)

SENSOR_NAME = 'omniscan'
SONAR_TOPIC_NAME = 'range'
SONAR_RAW_TOPIC_NAME = 'range_raw'

SENSOR_NUMBER = "450"
PORT_IP_ADDRESS = "192.168.2.92"
PORT_PORT = 51200
STARBOARD_IP_ADDRESS = "192.168.2.93"
STARBOARD_PORT = 51200
BOW_IP_ADDRESS = "192.168.2.94"
BOW_PORT = 51200
STERN_IP_ADDRESS = "192.168.2.95"
STERN_PORT = 51200

ALL_SONAR_DEFAULTS = dict(SONAR_PARAM_DEFAULTS)
ALL_SONAR_DEFAULTS['length_mm'] = 6000


def _populate_four_transducer_msgs(sonar_msg, sonar_raw_msg, stamp,
                                   port_data, port_scaled,
                                   starboard_data, starboard_scaled,
                                   bow_data, bow_scaled,
                                   stern_data, stern_scaled):
    sonar_raw_msg.header.stamp = stamp
    sonar_raw_msg.header.frame_id = "sonar"
    sonar_raw_msg.port_ping_number = port_data.ping_number
    sonar_raw_msg.starboard_ping_number = starboard_data.ping_number
    sonar_raw_msg.bow_ping_number = bow_data.ping_number
    sonar_raw_msg.stern_ping_number = stern_data.ping_number
    sonar_raw_msg.start_mm = port_data.start_mm
    sonar_raw_msg.length_mm = port_data.length_mm
    sonar_raw_msg.port_timestamp_ms = port_data.timestamp_ms
    sonar_raw_msg.starboard_timestamp_ms = starboard_data.timestamp_ms
    sonar_raw_msg.bow_timestamp_ms = bow_data.timestamp_ms
    sonar_raw_msg.stern_timestamp_ms = stern_data.timestamp_ms
    sonar_raw_msg.port_ping_hz = port_data.ping_hz
    sonar_raw_msg.starboard_ping_hz = starboard_data.ping_hz
    sonar_raw_msg.bow_ping_hz = bow_data.ping_hz
    sonar_raw_msg.stern_ping_hz = stern_data.ping_hz
    sonar_raw_msg.port_gain_index = port_data.gain_index
    sonar_raw_msg.starboard_gain_index = starboard_data.gain_index
    sonar_raw_msg.bow_gain_index = bow_data.gain_index
    sonar_raw_msg.stern_gain_index = stern_data.gain_index
    sonar_raw_msg.num_results = port_data.num_results
    sonar_raw_msg.sos_dmps = port_data.sos_dmps
    sonar_raw_msg.channel_number = port_data.channel_number
    sonar_raw_msg.port_pulse_duration_sec = port_data.pulse_duration_sec
    sonar_raw_msg.starboard_pulse_duration_sec = starboard_data.pulse_duration_sec
    sonar_raw_msg.bow_pulse_duration_sec = bow_data.pulse_duration_sec
    sonar_raw_msg.stern_pulse_duration_sec = stern_data.pulse_duration_sec
    sonar_raw_msg.port_analog_gain = port_data.analog_gain
    sonar_raw_msg.starboard_analog_gain = starboard_data.analog_gain
    sonar_raw_msg.bow_analog_gain = bow_data.analog_gain
    sonar_raw_msg.stern_analog_gain = stern_data.analog_gain
    sonar_raw_msg.port_max_pwr_db = port_data.max_pwr_db
    sonar_raw_msg.starboard_max_pwr_db = starboard_data.max_pwr_db
    sonar_raw_msg.bow_max_pwr_db = bow_data.max_pwr_db
    sonar_raw_msg.stern_max_pwr_db = stern_data.max_pwr_db
    sonar_raw_msg.port_min_pwr_db = port_data.min_pwr_db
    sonar_raw_msg.starboard_min_pwr_db = starboard_data.min_pwr_db
    sonar_raw_msg.bow_min_pwr_db = bow_data.min_pwr_db
    sonar_raw_msg.stern_min_pwr_db = stern_data.min_pwr_db
    sonar_raw_msg.port_transducer_heading_deg = port_data.transducer_heading_deg
    sonar_raw_msg.starboard_transducer_heading_deg = starboard_data.transducer_heading_deg
    sonar_raw_msg.bow_transducer_heading_deg = bow_data.transducer_heading_deg
    sonar_raw_msg.stern_transducer_heading_deg = stern_data.transducer_heading_deg
    sonar_raw_msg.vehicle_heading_deg = port_data.vehicle_heading_deg
    sonar_raw_msg.port_pwr_data = list(port_data.pwr_results)
    sonar_raw_msg.starboard_pwr_data = list(starboard_data.pwr_results)
    sonar_raw_msg.bow_pwr_data = list(bow_data.pwr_results)
    sonar_raw_msg.stern_pwr_data = list(stern_data.pwr_results)

    sonar_msg.header.stamp = stamp
    sonar_msg.header.frame_id = "sonar"
    sonar_msg.port_ping_number = port_data.ping_number
    sonar_msg.starboard_ping_number = starboard_data.ping_number
    sonar_msg.bow_ping_number = bow_data.ping_number
    sonar_msg.stern_ping_number = stern_data.ping_number
    sonar_msg.start_mm = port_data.start_mm
    sonar_msg.length_mm = port_data.length_mm
    sonar_msg.port_timestamp_ms = port_data.timestamp_ms
    sonar_msg.starboard_timestamp_ms = starboard_data.timestamp_ms
    sonar_msg.bow_timestamp_ms = bow_data.timestamp_ms
    sonar_msg.stern_timestamp_ms = stern_data.timestamp_ms
    sonar_msg.port_ping_hz = port_data.ping_hz
    sonar_msg.starboard_ping_hz = starboard_data.ping_hz
    sonar_msg.bow_ping_hz = bow_data.ping_hz
    sonar_msg.stern_ping_hz = stern_data.ping_hz
    sonar_msg.port_gain_index = port_data.gain_index
    sonar_msg.starboard_gain_index = starboard_data.gain_index
    sonar_msg.bow_gain_index = bow_data.gain_index
    sonar_msg.stern_gain_index = stern_data.gain_index
    sonar_msg.num_results = port_data.num_results
    sonar_msg.sos_dmps = port_data.sos_dmps
    sonar_msg.channel_number = port_data.channel_number
    sonar_msg.port_pulse_duration_sec = port_data.pulse_duration_sec
    sonar_msg.starboard_pulse_duration_sec = starboard_data.pulse_duration_sec
    sonar_msg.bow_pulse_duration_sec = bow_data.pulse_duration_sec
    sonar_msg.stern_pulse_duration_sec = stern_data.pulse_duration_sec
    sonar_msg.port_analog_gain = port_data.analog_gain
    sonar_msg.starboard_analog_gain = starboard_data.analog_gain
    sonar_msg.bow_analog_gain = bow_data.analog_gain
    sonar_msg.stern_analog_gain = stern_data.analog_gain
    sonar_msg.port_max_pwr_db = port_data.max_pwr_db
    sonar_msg.starboard_max_pwr_db = starboard_data.max_pwr_db
    sonar_msg.bow_max_pwr_db = bow_data.max_pwr_db
    sonar_msg.stern_max_pwr_db = stern_data.max_pwr_db
    sonar_msg.port_min_pwr_db = port_data.min_pwr_db
    sonar_msg.starboard_min_pwr_db = starboard_data.min_pwr_db
    sonar_msg.bow_min_pwr_db = bow_data.min_pwr_db
    sonar_msg.stern_min_pwr_db = stern_data.min_pwr_db
    sonar_msg.port_transducer_heading_deg = port_data.transducer_heading_deg
    sonar_msg.starboard_transducer_heading_deg = starboard_data.transducer_heading_deg
    sonar_msg.bow_transducer_heading_deg = bow_data.transducer_heading_deg
    sonar_msg.stern_transducer_heading_deg = stern_data.transducer_heading_deg
    sonar_msg.vehicle_heading_deg = port_data.vehicle_heading_deg
    sonar_msg.port_scaled_data = list(port_scaled)
    sonar_msg.starboard_scaled_data = list(starboard_scaled)
    sonar_msg.bow_scaled_data = list(bow_scaled)
    sonar_msg.stern_scaled_data = list(stern_scaled)


class SidescanAllNode(Node):
    def __init__(self):
        super().__init__('omniscanall')

        sensor_number = str(self.declare_parameter('sensor_number', int(SENSOR_NUMBER)).value)
        port_ip_address = str(self.declare_parameter('port_ip_address', PORT_IP_ADDRESS).value)
        port_port = self.declare_parameter('port_port', PORT_PORT).value
        starboard_ip_address = str(
            self.declare_parameter('starboard_ip_address', STARBOARD_IP_ADDRESS).value)
        starboard_port = self.declare_parameter('starboard_port', STARBOARD_PORT).value
        bow_ip_address = str(self.declare_parameter('bow_ip_address', BOW_IP_ADDRESS).value)
        bow_port = self.declare_parameter('bow_port', BOW_PORT).value
        stern_ip_address = str(self.declare_parameter('stern_ip_address', STERN_IP_ADDRESS).value)
        stern_port = self.declare_parameter('stern_port', STERN_PORT).value

        declare_sonar_params(self, ALL_SONAR_DEFAULTS)
        sonar_params = get_sonar_params(self)

        self.sensor_name = SENSOR_NAME + sensor_number
        self.range_raw_pub = self.create_publisher(
            SideScanSonarAllRaw, '/'.join([self.sensor_name, SONAR_RAW_TOPIC_NAME]), 10)
        self.range_pub = self.create_publisher(
            SideScanSonarAll, '/'.join([self.sensor_name, SONAR_TOPIC_NAME]), 10)

        logger = self.get_logger()
        self.omniscan450_port = Omniscan450Driver(
            ip_address=port_ip_address, port=port_port, logger=logger, **sonar_params)
        self.omniscan450_starboard = Omniscan450Driver(
            ip_address=starboard_ip_address, port=starboard_port, logger=logger, **sonar_params)
        self.omniscan450_bow = Omniscan450Driver(
            ip_address=bow_ip_address, port=bow_port, logger=logger, **sonar_params)
        self.omniscan450_stern = Omniscan450Driver(
            ip_address=stern_ip_address, port=stern_port, logger=logger, **sonar_params)

        self.drivers = [
            self.omniscan450_port,
            self.omniscan450_starboard,
            self.omniscan450_bow,
            self.omniscan450_stern,
        ]
        self.add_on_set_parameters_callback(make_param_callback(self.drivers, self))

        self.first_exception_logged = False
        self._timer = self.create_timer(
            timer_period_sec(sonar_params['msec_per_ping']), self._poll_callback)

        time.sleep(1)

    def _poll_callback(self):
        current_time = self.get_clock().now().to_msg()

        try:
            port_data, port_scaled_results = self.omniscan450_port.get_data()
            starboard_data, starboard_scaled_results = self.omniscan450_starboard.get_data()
            bow_data, bow_scaled_results = self.omniscan450_bow.get_data()
            stern_data, stern_scaled_results = self.omniscan450_stern.get_data()

            if any(d is None for d in [port_data, starboard_data, bow_data, stern_data]):
                return

            sonar_msg = SideScanSonarAll()
            sonar_raw_msg = SideScanSonarAllRaw()
            _populate_four_transducer_msgs(
                sonar_msg, sonar_raw_msg, current_time,
                port_data, port_scaled_results,
                starboard_data, starboard_scaled_results,
                bow_data, bow_scaled_results,
                stern_data, stern_scaled_results)

            self.range_raw_pub.publish(sonar_raw_msg)
            self.range_pub.publish(sonar_msg)
            self.first_exception_logged = False

        except Exception:
            if not self.first_exception_logged:
                self.get_logger().error('Exception when reading Omniscan450 sonar data.')
                self.first_exception_logged = True

    def destroy_node(self):
        for driver in self.drivers:
            driver.close_connection()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = SidescanAllNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
