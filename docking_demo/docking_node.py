import math
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist

from docking_demo.pose_utils import quaternion_to_yaw, normalize_angle
from docking_demo.controllers import ProportionalController


# Distance (m) at which robot_2 counts as "docked"
DOCK_DISTANCE = 0.0

# robot_1 roaming speed
ROAM_LINEAR_SPEED = 0.20
ROAM_ANGULAR_SPEED = 0.25

# robot_2 docking speed and steering
DOCK_LINEAR_SPEED = 0.15
TURN_GAIN = 0.8
HEADING_TOLERANCE = 0.25  # radians - turn first if error > this


class DockingNode(Node):

    def __init__(self):
        super().__init__('docking_node')

        self.poses = {}
        self.is_docked = False
        self.steer_ctrl = ProportionalController(kp=TURN_GAIN)

        self.create_subscription(Odometry, '/robot_1/odom',
            lambda msg: self.update_pose('robot_1', msg), 10)
        self.create_subscription(Odometry, '/robot_2/odom',
            lambda msg: self.update_pose('robot_2', msg), 10)

        self.pub_robot1 = self.create_publisher(Twist, '/robot_1/cmd_vel', 10)
        self.pub_robot2 = self.create_publisher(Twist, '/robot_2/cmd_vel', 10)

        self.create_timer(0.1, self.control_loop)

    def update_pose(self, robot_name, odom_msg):
        pos = odom_msg.pose.pose.position
        yaw = quaternion_to_yaw(odom_msg.pose.pose.orientation)
        self.poses[robot_name] = (pos.x, pos.y, yaw)

    def control_loop(self):
        if 'robot_1' not in self.poses or 'robot_2' not in self.poses:
            return

        self.roam()

        if not self.is_docked:
            self.dock()

    def roam(self):
        cmd = Twist()
        if not self.is_docked:
            cmd.linear.x = ROAM_LINEAR_SPEED
            cmd.angular.z = ROAM_ANGULAR_SPEED
        self.pub_robot1.publish(cmd)

    def dock(self):
        target = self.poses['robot_1']
        follower = self.poses['robot_2']

        dx = target[0] - follower[0]
        dy = target[1] - follower[1]
        distance = math.hypot(dx, dy)

        if distance <= DOCK_DISTANCE:
            self.pub_robot2.publish(Twist())
            self.is_docked = True
            self.get_logger().info('DOCKED: robot_2 has connected with robot_1')
            return

        heading_error = normalize_angle(math.atan2(dy, dx) - follower[2])

        cmd = Twist()
        if abs(heading_error) > HEADING_TOLERANCE:
            cmd.linear.x = 0.0
        else:
            cmd.linear.x = DOCK_LINEAR_SPEED
        cmd.angular.z = self.steer_ctrl.apply(heading_error)

        self.pub_robot2.publish(cmd)
        self.get_logger().info(
            f'robot_2 -> robot_1 | distance={distance:.2f} m',
            throttle_duration_sec=1.0)


def main():
    rclpy.init()
    node = DockingNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()