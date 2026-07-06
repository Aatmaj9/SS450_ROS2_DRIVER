"""Shared parameter helpers for Omniscan450 sidescan nodes."""

from rcl_interfaces.msg import SetParametersResult
from rclpy.parameter import Parameter

SONAR_PARAM_DEFAULTS = {
    'speed_of_sound_mm': 1482000,
    'start_mm': 0,
    'length_mm': 5000,
    'msec_per_ping': 0,
    'pulse_len_percent': 0.002,
    'filter_duration_percent': 0.0015,
    'gain_index': -1,
    'num_results': 600,
}

SONAR_PARAM_RANGES = {
    'speed_of_sound_mm': (1482000, 1500000),
    'start_mm': (0, 5000),
    'length_mm': (0, 300000),
    'msec_per_ping': (0, 10),
    'pulse_len_percent': (0.002, 0.004),
    'filter_duration_percent': (0.0015, 0.0016),
    'gain_index': (-1, 7),
    'num_results': (200, 1200),
}


def declare_sonar_params(node, defaults=None):
    """Declare tunable sonar parameters on a ROS2 node."""
    params = defaults or SONAR_PARAM_DEFAULTS
    for name, value in params.items():
        node.declare_parameter(name, value)
    return params


def get_sonar_params(node):
    """Read current sonar parameter values from the node."""
    return {name: node.get_parameter(name).value for name in SONAR_PARAM_DEFAULTS}


def validate_sonar_param(param):
    """Validate a single sonar parameter against allowed ranges."""
    if param.name not in SONAR_PARAM_RANGES:
        return True

    low, high = SONAR_PARAM_RANGES[param.name]
    value = param.value

    if param.type_ == Parameter.Type.INTEGER:
        if not isinstance(value, int):
            return False
        return low <= value <= high

    if param.type_ == Parameter.Type.DOUBLE:
        if not isinstance(value, (int, float)):
            return False
        return low <= float(value) <= high

    return False


def make_param_callback(drivers, node):
    """Create a parameter callback that updates all connected sonar drivers."""
    def _on_set_params(params):
        for param in params:
            if not validate_sonar_param(param):
                return SetParametersResult(
                    successful=False,
                    reason='Parameter %s out of range' % param.name,
                )

        config = get_sonar_params(node)
        for driver in drivers:
            driver.set_parameters(config)

        return SetParametersResult(successful=True)

    return _on_set_params


def timer_period_sec(msec_per_ping):
    """Convert msec_per_ping to a ROS2 timer period."""
    if msec_per_ping <= 0:
        return 0.001
    return msec_per_ping / 1000.0
