#!/usr/bin/env python3

"""
  Author: Monika Roznere
  Affiliation: Binghamton University
  Date: 07/19/2025

  Description:
  Class for interacting with Omniscan 450 Side Scan Sonar.
"""

import time

from brping import definitions
from brping import Omniscan450

SONAR_IP_ADDRESS = "192.168.2.92"
SONAR_PORT = 51200
SPEED_OF_SOUND_MM = 1482000
START_MM = 0
LENGTH_MM = 5000
MSEC_PER_PING = 0
PULSE_LEN_PERCENT = 0.002
FILTER_DURATION_PERCENT = 0.0015
GAIN_INDEX = -1
NUM_RESULTS = 600
CONNECT_TIMEOUT_SEC = 5.0
RETRY_INTERVAL_SEC = 5.0


class Omniscan450Driver:
    def __init__(self, ip_address=SONAR_IP_ADDRESS, port=SONAR_PORT,
                 speed_of_sound_mm=SPEED_OF_SOUND_MM, start_mm=START_MM, length_mm=LENGTH_MM,
                 msec_per_ping=MSEC_PER_PING, pulse_len_percent=PULSE_LEN_PERCENT,
                 filter_duration_percent=FILTER_DURATION_PERCENT,
                 gain_index=GAIN_INDEX, num_results=NUM_RESULTS, logger=None,
                 connect_timeout_sec=CONNECT_TIMEOUT_SEC,
                 retry_interval_sec=RETRY_INTERVAL_SEC):

        self.ip_address = ip_address
        self.port = port
        self.logger = logger
        self.connect_timeout_sec = connect_timeout_sec
        self.retry_interval_sec = retry_interval_sec
        self._last_connect_attempt = 0.0
        self._configured = False

        self.speed_of_sound_mm = speed_of_sound_mm
        self.start_mm = start_mm
        self.length_mm = length_mm
        self.msec_per_ping = msec_per_ping
        self.pulse_len_percent = pulse_len_percent
        self.filter_duration_percent = filter_duration_percent
        self.gain_index = gain_index
        self.num_results = num_results

        self.omniscan450 = Omniscan450()
        self.connect()

    @property
    def is_connected(self):
        return self.omniscan450.iodev is not None

    def _log(self, message, level='info'):
        if self.logger is not None:
            getattr(self.logger, level)(message)
        else:
            print(message)

    def connect(self):
        """Try to open a TCP connection to the sonar. Returns True on success."""
        now = time.monotonic()
        if now - self._last_connect_attempt < self.retry_interval_sec:
            return self.is_connected

        self._last_connect_attempt = now

        if self.omniscan450.iodev is not None:
            try:
                self.omniscan450.iodev.close()
            except Exception:
                pass
            self.omniscan450.iodev = None
            self._configured = False

        try:
            self.omniscan450.connect_tcp(
                self.ip_address, self.port, timeout=self.connect_timeout_sec)
        except Exception as exc:
            self._log(
                f'Unable to connect to Omniscan at {self.ip_address}:{self.port} — {exc}',
                level='warn')
            return False

        if self.omniscan450.initialize() is False:
            self._log(f'Omniscan at {self.ip_address} failed to initialize', level='warn')
            return False

        data = self.omniscan450.readDeviceInformation()
        if data is None:
            self._log(f'Omniscan at {self.ip_address} did not return device information',
                      level='warn')
            return False

        self._log(f'Connected to Omniscan at {self.ip_address} — device type: {data.device_type}')
        self._set_sidescan_params(change_speed_of_sound=True, change_os_ping_params=True)
        self._configured = True
        return True

    def get_data(self):
        """Get data from the sonar and return raw data and scaled result."""
        if not self.is_connected and not self.connect():
            return None, None

        data = self.omniscan450.wait_message([definitions.OMNISCAN450_OS_MONO_PROFILE])
        if not data:
            self._log(
                f'Omniscan at {self.ip_address} failed to get message — will reconnect',
                level='warn')
            self._drop_connection()
            return None, None

        scaled_results = Omniscan450.scale_power(data)
        if len(scaled_results) == 0:
            self._log(f'Omniscan at {self.ip_address}: length of scaled result is 0',
                      level='warn')

        return data, scaled_results

    def _drop_connection(self):
        if self.omniscan450.iodev is not None:
            try:
                self.omniscan450.iodev.close()
            except Exception:
                pass
        self.omniscan450.iodev = None
        self._configured = False

    def set_parameters(self, config):
        """Set parameters from a dict of sonar tuning values."""
        change_speed_of_sound = False
        if self.speed_of_sound_mm != config['speed_of_sound_mm']:
            self.speed_of_sound_mm = config['speed_of_sound_mm']
            change_speed_of_sound = True

        change_os_ping_params = False
        if self.start_mm != config['start_mm']:
            self.start_mm = config['start_mm']
            change_os_ping_params = True

        if self.length_mm != config['length_mm']:
            self.length_mm = config['length_mm']
            change_os_ping_params = True

        if self.msec_per_ping != config['msec_per_ping']:
            self.msec_per_ping = config['msec_per_ping']
            change_os_ping_params = True

        if self.pulse_len_percent != config['pulse_len_percent']:
            self.pulse_len_percent = config['pulse_len_percent']
            change_os_ping_params = True

        if self.filter_duration_percent != config['filter_duration_percent']:
            self.filter_duration_percent = config['filter_duration_percent']
            change_os_ping_params = True

        if self.gain_index != config['gain_index']:
            self.gain_index = config['gain_index']
            change_os_ping_params = True

        if self.num_results != config['num_results']:
            self.num_results = config['num_results']
            change_os_ping_params = True

        if self.is_connected:
            self._set_sidescan_params(change_speed_of_sound, change_os_ping_params)
        return config

    def _set_sidescan_params(self, change_speed_of_sound=False, change_os_ping_params=False):
        if not self.is_connected:
            return

        if change_speed_of_sound:
            self.omniscan450.control_set_speed_of_sound(
                speed_of_sound=self.speed_of_sound_mm
            )

        if change_os_ping_params:
            self.omniscan450.control_os_ping_params(
                start_mm=self.start_mm,
                length_mm=self.length_mm,
                msec_per_ping=self.msec_per_ping,
                pulse_len_percent=self.pulse_len_percent,
                filter_duration_percent=self.filter_duration_percent,
                gain_index=self.gain_index,
                num_results=self.num_results,
                enable=1,
                reserved_1=0,
                reserved_2=0,
                reserved_3=0,
            )

        time.sleep(0.01)

    def close_connection(self):
        if not self.is_connected:
            return

        try:
            self.omniscan450.control_os_ping_params(
                start_mm=self.start_mm,
                length_mm=self.length_mm,
                msec_per_ping=self.msec_per_ping,
                pulse_len_percent=self.pulse_len_percent,
                filter_duration_percent=self.filter_duration_percent,
                gain_index=self.gain_index,
                num_results=self.num_results,
                enable=0,
                reserved_1=0,
                reserved_2=0,
                reserved_3=0,
            )
        except Exception as exc:
            self._log(f'Failed to disable pings on {self.ip_address}: {exc}', level='warn')

        self._drop_connection()
