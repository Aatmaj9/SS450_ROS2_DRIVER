'use strict';

const params = new URLSearchParams(window.location.search);
const ROSBRIDGE_PORT = params.get('rosbridge_port') || '9090';
const TOPIC_NAME = params.get('topic') || '/omniscan450/range';
const MAX_ROWS = parseInt(params.get('max_rows') || '512', 10);

const rosbridgeUrl = `ws://${window.location.hostname}:${ROSBRIDGE_PORT}`;
document.getElementById('rosbridge-url').textContent = rosbridgeUrl;
document.getElementById('web-port').textContent = window.location.port || '9001';

const rosStatusEl = document.getElementById('ros-status');
const pingInfoEl = document.getElementById('ping-info');

/** Map scaled dB to RGB using a sonar-style colormap. */
function dbToRgb(value, minDb, maxDb) {
  let t = (value - minDb) / (maxDb - minDb);
  if (!Number.isFinite(t)) {
    t = 0;
  }
  t = Math.max(0, Math.min(1, t));

  // Dark blue → cyan → yellow → white
  const r = Math.floor(255 * Math.max(0, Math.min(1, (t - 0.5) * 2)));
  const g = Math.floor(255 * Math.max(0, Math.min(1, t * 1.4)));
  const b = Math.floor(255 * Math.max(0, Math.min(1, 1 - t * 1.2)));
  return [r, g, b];
}

class WaterfallPlot {
  constructor(canvas, maxRows) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d', { alpha: false });
    this.maxRows = maxRows;
    this.width = 0;
    this.height = maxRows;
    this.rangeLabel = '';
  }

  clear() {
    if (this.width > 0) {
      this.ctx.fillStyle = '#010409';
      this.ctx.fillRect(0, 0, this.width, this.height);
    }
  }

  addRow(samples, minDb, maxDb, startMm, lengthMm) {
    const n = samples.length;
    if (n === 0) {
      return;
    }

    if (this.width !== n) {
      this.width = n;
      this.canvas.width = n;
      this.canvas.height = this.height;
      this.clear();
    }

    this.rangeLabel = `${(startMm / 1000).toFixed(1)}–${((startMm + lengthMm) / 1000).toFixed(1)} m`;

    // Scroll existing image down by one row.
    this.ctx.drawImage(
      this.canvas,
      0, 0, this.width, this.height - 1,
      0, 1, this.width, this.height - 1
    );

    const imageData = this.ctx.createImageData(n, 1);
    const data = imageData.data;

    for (let i = 0; i < n; i++) {
      const [r, g, b] = dbToRgb(samples[i], minDb, maxDb);
      const idx = i * 4;
      data[idx] = r;
      data[idx + 1] = g;
      data[idx + 2] = b;
      data[idx + 3] = 255;
    }

    this.ctx.putImageData(imageData, 0, 0);
  }
}

const portPlot = new WaterfallPlot(document.getElementById('port-canvas'), MAX_ROWS);
const starboardPlot = new WaterfallPlot(document.getElementById('starboard-canvas'), MAX_ROWS);

document.getElementById('clear-btn').addEventListener('click', () => {
  portPlot.clear();
  starboardPlot.clear();
});

function setRosStatus(connected, text) {
  rosStatusEl.textContent = text;
  rosStatusEl.classList.toggle('connected', connected);
  rosStatusEl.classList.toggle('disconnected', !connected);
}

const ros = new ROSLIB.Ros({
  url: rosbridgeUrl,
  groovyCompatibilityMode: false,
});

let rangeTopic = null;

function subscribeToRange() {
  if (rangeTopic) {
    rangeTopic.unsubscribe();
  }

  rangeTopic = new ROSLIB.Topic({
    ros,
    name: TOPIC_NAME,
    messageType: 'sidescan_ros2/msg/SideScanSonar',
    compression: 'none',
  });

  rangeTopic.subscribe((msg) => {
    const portData = msg.port_scaled_data || [];
    const starboardData = msg.starboard_scaled_data || [];

    portPlot.addRow(
      portData,
      msg.port_min_pwr_db,
      msg.port_max_pwr_db,
      msg.start_mm,
      msg.length_mm
    );

    starboardPlot.addRow(
      starboardData,
      msg.starboard_min_pwr_db,
      msg.starboard_max_pwr_db,
      msg.start_mm,
      msg.length_mm
    );

    pingInfoEl.textContent =
      `Port ping #${msg.port_ping_number} · Starboard ping #${msg.starboard_ping_number} · ` +
      `${portData.length} bins · ${portPlot.rangeLabel}`;
  });
}

ros.on('connection', () => {
  setRosStatus(true, 'ROS: connected');
  subscribeToRange();
});

ros.on('error', () => {
  setRosStatus(false, 'ROS: error');
});

ros.on('close', () => {
  setRosStatus(false, 'ROS: disconnected');
});
