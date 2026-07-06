# SS450 ROS 2 Driver

ROS 2 driver for the **[Cerulean Omniscan 450 SS](https://ceruleansonar.com/product/omniscan-450ss-300m/)** side-scan sonar.

The package connects to one or more Omniscan 450 SS transducers over Ethernet, streams acoustic range profiles, and publishes them as ROS 2 messages. It includes an optional browser-based waterfall viewer for real-time side-scan visualization.

| | |
|---|---|
| **ROS package** | `SS450_ros2_driver` |
| **ROS distro** | Humble (tested) |
| **Protocol** | [Cerulean Ping Protocol](https://docs.ceruleansonar.com/c/v/omniscan-450/appendix-a-programming-api) over TCP port `51200` |
| **License** | MIT |

---

## About the Omniscan 450 SS

The [Omniscan 450 SS](https://ceruleansonar.com/product/omniscan-450ss-300m/) is a traditional side-scan sonar from [Cerulean Sonar](https://ceruleansonar.com/), designed for seafloor imaging, search and recovery, marine archaeology, and habitat mapping. Each unit consists of a separate transducer and electronics module connected by cable.

Typical applications pair **two transducers** — one mounted on the port side and one on starboard — to scan both sides of a vehicle simultaneously.

### Key specifications

| Parameter | Value |
|---|---|
| Frequency | 450 kHz (nominal) |
| Maximum range | 150 m |
| Range resolution | Up to 1/1200 of range setting |
| Beam width | 0.5° (along-track) |
| Beam height | 50° |
| Maximum ping rate | 20 Hz |
| Max operating depth | 300 m (transducer) |
| Data interface | 100Base-T Ethernet |
| Power | 10–30 V DC, up to 10 W while pinging |

### Product & documentation links

- [Omniscan 450 SS product page (Cerulean)](https://ceruleansonar.com/product/omniscan-450ss-300m/)
- [Omniscan 450 SS for BlueBoat (Blue Robotics store)](https://bluerobotics.com/store/the-reef/cerulean-sidescan-sonar/)
- [Omniscan 450 specifications](https://docs.ceruleansonar.com/c/omniscan-450/specifications)
- [Programming API / Ping Protocol](https://docs.ceruleansonar.com/c/v/omniscan-450/appendix-a-programming-api)
- [BlueBoat integration guide](https://bluerobotics.com/learn/omniscan-450-ss-integration/)

> **Note:** Cerulean's [SonarView](https://ceruleansonar.com/) application provides official visualization and logging. This ROS 2 driver is for integrating Omniscan 450 SS data into robotic systems, autonomy stacks, and custom processing pipelines.

---

## Features

- **Dual-transducer support** — synchronizes port and starboard pings into a single message pair
- **Quad-transducer support** — port, starboard, bow, and stern in one node (`sidescan_all_node`)
- **Live parameter tuning** — adjust gain, range window, ping rate, and more at runtime via ROS 2 parameters
- **Raw and scaled output** — publish both corrected dB profiles and raw uint16 power values
- **Built-in waterfall viewer** — optional web UI with rosbridge for live side-scan display
- **Auto-reconnect** — driver retries connection if a transducer is temporarily unreachable
- **Vendored `brping` library** — no external ping-python install required

---

## Hardware setup

1. Power each Omniscan 450 SS electronics module (10–30 V DC).
2. Connect each module to your network via Ethernet (100Base-T).
3. Assign a static IP to each transducer on the same subnet as your ROS 2 machine (e.g. `192.168.2.x`).
4. Verify connectivity before launching the driver:

```bash
ping 192.168.2.93   # port transducer
ping 192.168.2.95   # starboard transducer
```

Default launch files assume TCP port **51200** on each device. Adjust IP addresses in the launch arguments to match your network.

For BlueBoat deployments, follow the [BlueBoat integration guide](https://bluerobotics.com/learn/omniscan-450-ss-integration/) for physical mounting and network configuration.

---

## Requirements

- [ROS 2 Humble](https://docs.ros.org/en/humble/)
- `python3-serial`
- `colcon` build tools

Optional (for the waterfall web viewer):

```bash
sudo apt install ros-humble-rosbridge-server
```

---

## Installation

Clone this repository into your ROS 2 workspace `src` directory:

```bash
cd ~/ros2_ws/src
git clone https://github.com/Aatmaj9/SS450_ros2_driver.git
cd ~/ros2_ws
```

Build and source:

```bash
colcon build --packages-select SS450_ros2_driver
source install/setup.bash
```

---

## Usage

### Driver only — port + starboard (2 transducers)

```bash
ros2 launch SS450_ros2_driver sidescan.launch.py
```

Override transducer IP addresses:

```bash
ros2 launch SS450_ros2_driver sidescan.launch.py \
  port_ip_address:=192.168.2.93 \
  starboard_ip_address:=192.168.2.95
```

### Driver + waterfall web viewer

Starts the driver, [rosbridge](http://wiki.ros.org/rosbridge_server) (WebSocket on port 9090), and a static web server on port **9001**:

```bash
ros2 launch SS450_ros2_driver sidescan_waterfall.launch.py
```

Open in a browser:

```
http://localhost:9001/
```

### Four transducers — port, starboard, bow, stern

```bash
ros2 launch SS450_ros2_driver sidescan_all.launch.py
```

Override all four IPs:

```bash
ros2 launch SS450_ros2_driver sidescan_all.launch.py \
  port_ip_address:=192.168.2.94 \
  starboard_ip_address:=192.168.2.95 \
  bow_ip_address:=192.168.2.93 \
  stern_ip_address:=192.168.2.92
```

---

## Launch arguments

### `sidescan.launch.py` / `sidescan_waterfall.launch.py`

| Argument | Default | Description |
|---|---|---|
| `sensor_number` | `450` | Sensor ID used in node name and topic prefix |
| `port_ip_address` | `192.168.2.93` | IP of the port-side transducer |
| `port_port` | `51200` | TCP port for port transducer |
| `starboard_ip_address` | `192.168.2.95` | IP of the starboard-side transducer |
| `starboard_port` | `51200` | TCP port for starboard transducer |
| `config_file` | `config/omniscan450_params.yaml` | Default sonar parameter file |
| `web_port` | `9001` | HTTP port for waterfall viewer (waterfall launch only) |
| `rosbridge_port` | `9090` | WebSocket port for rosbridge (waterfall launch only) |

### `sidescan_all.launch.py`

Adds `bow_ip_address`, `bow_port`, `stern_ip_address`, and `stern_port` with defaults in `config/omniscan450_all_params.yaml`.

---

## ROS topics

### Two-transducer mode (`sidescan_node`)

| Topic | Message type | Description |
|---|---|---|
| `/omniscan450/range` | `SS450_ros2_driver/msg/SideScanSonar` | Scaled dB range profiles (port + starboard) |
| `/omniscan450/range_raw` | `SS450_ros2_driver/msg/SideScanSonarRaw` | Raw uint16 power values (port + starboard) |

### Four-transducer mode (`sidescan_all_node`)

Uses the same topic names as the two-transducer node, but publishes the four-transducer message types:

| Topic | Message type | Description |
|---|---|---|
| `/omniscan450/range` | `SS450_ros2_driver/msg/SideScanSonarAll` | Scaled dB profiles (port, starboard, bow, stern) |
| `/omniscan450/range_raw` | `SS450_ros2_driver/msg/SideScanSonarAllRaw` | Raw uint16 power values (all four transducers) |

> Only run one driver node at a time — the two- and four-transducer nodes publish on the same topic names with different message types.

Each message contains synchronized ping metadata (ping number, timestamps, gain, heading) and a 1D cross-track intensity array per transducer. The `range` topic carries log-scaled, corrected values; `range_raw` carries the raw ADC counts from the sonar.

Inspect live data:

```bash
ros2 topic echo /omniscan450/range --no-arr
ros2 topic hz /omniscan450/range
```

---

## Runtime parameters

Sonar parameters can be changed while the node is running. Updates are applied to all connected transducers.

```bash
ros2 param set /omniscan450 gain_index 3
ros2 param set /omniscan450 length_mm 6000
ros2 param set /omniscan450 num_results 800
```

| Parameter | Default | Range | Description |
|---|---|---|---|
| `speed_of_sound_mm` | `1482000` | 1482000–1500000 | Speed of sound in mm/s |
| `start_mm` | `0` | 0–5000 | Start of scan window from transducer (mm) |
| `length_mm` | `5000` | 0–300000 | Length of scan window (mm) |
| `msec_per_ping` | `0` | 0–10 | Minimum interval between pings (0 = as fast as possible) |
| `pulse_len_percent` | `0.002` | 0.002–0.004 | Transmit pulse length as fraction of range |
| `filter_duration_percent` | `0.0015` | 0.0015–0.0016 | Receive filter duration as fraction of range |
| `gain_index` | `-1` | -1–7 | Receiver gain index (-1 = auto) |
| `num_results` | `600` | 200–1200 | Number of range bins per ping |

Defaults are defined in `config/omniscan450_params.yaml` and `config/omniscan450_all_params.yaml`. For protocol-level details on each parameter, see the [Omniscan 450 programming API](https://docs.ceruleansonar.com/c/v/omniscan-450/appendix-a-programming-api).

---

## Related projects

A companion driver for the Omniscan 450 **forward-scan (FS)** variant is available separately as `FS450_ros2_driver`.

---

## Author

**Aatmaj Bhayani** — Marine Autonomous Vehicles Lab (MAV-Lab), IIT Madras

## License

MIT — see [LICENSE](LICENSE) for details.

## Acknowledgments

- [Monika Roznere](https://monikaroznere.com) and the Marine Robotics Lab, Binghamton University, for the original ROS 1 [`omniscan_sidescan`](https://github.com/bing-marine-robotics-lab/omniscan_sidescan) package that this driver is based on
- [Cerulean Sonar](https://ceruleansonar.com/) for the Omniscan 450 hardware and Ping Protocol
- [Blue Robotics](https://bluerobotics.com/) for the `ping-python` / `brping` library foundation
