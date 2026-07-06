# Raw data from side scan sonar.
std_msgs/Header header

uint32 port_ping_number      # Sequentially assigned from 0 at power up
uint32 starboard_ping_number
uint32 bow_ping_number
uint32 stern_ping_number
uint32 start_mm         # The beginning of the scan region in mm from the transducer
uint32 length_mm        # The length of the scan region
uint32 port_timestamp_ms     # msec since power up at time of ping
uint32 starboard_timestamp_ms
uint32 bow_timestamp_ms
uint32 stern_timestamp_ms
uint32 port_ping_hz          # Frequency of acoustic signal
uint32 starboard_ping_hz
uint32 bow_ping_hz
uint32 stern_ping_hz
uint16 port_gain_index       # 0-7
uint16 starboard_gain_index
uint16 bow_gain_index
uint16 stern_gain_index
uint16 num_results      # Length of pwr_results array
uint16 sos_dmps         # Speed of sound, decimeters/sec
uint8 channel_number
# uint8 reserved
float32 port_pulse_duration_sec
float32 starboard_pulse_duration_sec
float32 bow_pulse_duration_sec
float32 stern_pulse_duration_sec
float32 port_analog_gain
float32 starboard_analog_gain
float32 bow_analog_gain
float32 stern_analog_gain
float32 port_max_pwr_db
float32 starboard_max_pwr_db
float32 bow_max_pwr_db
float32 stern_max_pwr_db
float32 port_min_pwr_db
float32 starboard_min_pwr_db
float32 bow_min_pwr_db
float32 stern_min_pwr_db
float32 port_transducer_heading_deg
float32 starboard_transducer_heading_deg
float32 bow_transducer_heading_deg
float32 stern_transducer_heading_deg
float32 vehicle_heading_deg


uint16[] port_pwr_data
uint16[] starboard_pwr_data
uint16[] bow_pwr_data
uint16[] stern_pwr_data
