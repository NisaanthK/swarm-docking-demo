# Swarm Docking Demo

Proof-of-concept for autonomous robot-to-robot docking, built for the
Intelligent Robotics swarm project (Group 7).

## What this is

Two TurtleBot3 robots spawn in Gazebo Classic, ~2 metres apart.

- **robot_1** = the docking target (leader)
- **robot_2** = drives toward robot_1 using its odometry, turns to
  face it, approaches, and stops once it's within 0.4 m -- printing
  `DOCKED!` when it succeeds.

This demonstrates the core "physical connection between robots"
behaviour requested by Marco, as a platform-independent proof of
concept (Gazebo Classic, since Ignition/Marco's full stack needs more
GPU power than our machines have).

## Project structure

```
docking_demo/
├── docking_demo/
│   ├── docking_node.py    <- main node: decides when/how to dock
│   ├── pose_utils.py       <- math helpers (quaternion -> yaw, angle wrap)
│   └── controllers.py      <- simple steering controller
├── launch/
│   └── docking_world.launch.py   <- spawns Gazebo + both robots
├── models/
│   └── turtlebot3_burger_hex/    <- TurtleBot3 model with a hex marker on top
└── setup.py / package.xml
```

## One-time setup

Only needed the first time you set this up on a new machine.

```bash
cd ~/ros2_ws/src
git clone https://github.com/NisaanthK/swarm-docking-demo.git docking_demo
cd ~/ros2_ws
colcon build --packages-select docking_demo
```

## How to run it (every time)

You need **two terminals**, both inside the `~/ros2_ws` workspace.

### Terminal 1 -- start the simulation

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

export GAZEBO_PLUGIN_PATH=/opt/ros/humble/lib:$GAZEBO_PLUGIN_PATH
export TURTLEBOT3_MODEL=burger

ros2 launch docking_demo docking_world.launch.py
```

- This opens Gazebo with both robots.
- **Wait until both robots are visible** before moving on -- spawning
  can take up to ~1-2 minutes on WSL2.
- Leave this terminal running.

### Terminal 2 -- run the docking node

Open a new terminal tab/window.

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run docking_demo docking_node
```

You should see:

```
[INFO] [docking_node]: robot_2 -> robot_1 | distance=1.60 m
[INFO] [docking_node]: robot_2 -> robot_1 | distance=1.41 m
...
[INFO] [docking_node]: DOCKED: robot_2 has connected with robot_1
```

In Gazebo, robot_2 will drive toward robot_1 and stop once docked.

## Stopping everything

In each terminal, press `Ctrl+C`. If Gazebo doesn't fully close:

```bash
pkill -9 gzserver gzclient
```

## Notes / known issues

- **First-time spawn can take ~1-2 minutes** -- this is a WSL2 +
  Gazebo Classic quirk, not an error. If it errors with
  `Service /spawn_entity unavailable`, the spawn simply needs more
  time than the default 30s timeout.
- The robots may jitter slightly after docking -- this is just their
  collision boxes touching, not a bug.

## Reference

Steering controller structure loosely inspired by:
https://github.com/silvery107/auto-docking-vessels

## Next steps / integration with Marco's swarm stack

Right now this runs as a standalone package. The natural next step is
to swap the `/robot_X/odom` subscriptions for Marco's
`/swarm/robot_states` topic (which already provides each robot's
x, y, yaw, role, and leader_id), so docking becomes an extra behaviour
inside the existing relay-tree/formation system instead of a separate
script.
