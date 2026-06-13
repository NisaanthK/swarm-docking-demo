import math


def quaternion_to_yaw(orientation):
    """Convert a quaternion into a yaw angle (in radians)."""
    siny = 2.0 * (orientation.w * orientation.z + orientation.x * orientation.y)
    cosy = 1.0 - 2.0 * (orientation.y ** 2 + orientation.z ** 2)
    return math.atan2(siny, cosy)


def normalize_angle(angle):
    return math.atan2(math.sin(angle), math.cos(angle))