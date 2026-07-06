# Raspberry Pi 5 Ethernet Configuration for Ethernet Devices on Ethernet Switch

## Platform

- **Hardware:** Raspberry Pi 5
- **Operating System:** Ubuntu 24.04.3 LTS (Noble Numbat)

# Step 1: Configure Netplan to use NetworkManager

Edit the Netplan configuration.

```bash
sudo nano /etc/netplan/*.yaml
```

Add the **renderer** field near the top.

Example:

```yaml
network:
  version: 2
  renderer: NetworkManager

  wifis:
    wlan0:
      optional: true
      dhcp4: true
      access-points:
        "mavlab":
          auth:
            key-management: psk
            password: "<PASSWORD>"

    wlxdc6279486c49:
      optional: true
      dhcp4: true
      dhcp6: false
      access-points:
        "mavlab":
          auth:
            key-management: psk
            password: "<PASSWORD>"
```

> **Note:** Keep your Wi-Fi configuration unchanged. Only add `renderer: NetworkManager`.

---

# Step 2: Allow NetworkManager to Manage Interfaces

Edit:

```bash
sudo nano /etc/NetworkManager/NetworkManager.conf
```

Change

```ini
[main]
plugins=ifupdown,keyfile

[ifupdown]
managed=false

[device]
wifi.scan-rand-mac-address=no
```

to

```ini
[main]
plugins=ifupdown,keyfile

[ifupdown]
managed=true

[device]
wifi.scan-rand-mac-address=no
```

---

# Step 3: Apply the Changes

```bash
sudo netplan apply
```

> **Important:**  
> SSH over Wi-Fi may disconnect for a few seconds while the networking backend switches to NetworkManager.
>
> This is expected.
>
> Simply reconnect via SSH after a few seconds.

Restart NetworkManager:

```bash
sudo systemctl restart NetworkManager
```

---

# Step 4: Verify NetworkManager

```bash
nmcli device status
```

`eth0` should **not** be listed as **unmanaged**.

---

# Step 5: Create the Static Ethernet Connection

Create a static Ethernet connection for the sonar network.

```bash
sudo nmcli connection add \
    type ethernet \
    con-name eth_switch \
    ifname eth0 \
    ipv4.method manual \
    ipv4.addresses 192.168.2.10/24
```
> **Important:**  
> Set the ip to whatever static ip your sonar devices are set to.

---

# Step 6: Enable Auto-connect

```bash
sudo nmcli connection modify eth_switch connection.autoconnect yes
```

---

# Step 7: Bring the Connection Up

```bash
sudo nmcli connection up eth_switch
```

---

# Step 8: Verify Configuration

Verify IP address:

```bash
ip addr show eth0
```

Expected:

```
inet 192.168.2.10/24
```

Verify routing:

```bash
ip route
```

Expected route:

```
192.168.2.0/24 dev eth0
```

Verify NetworkManager:

```bash
nmcli device status
```

Expected:

```
DEVICE   TYPE      STATE      CONNECTION

wlan0    wifi      connected  netplan-wlan0-mavlab
eth0     ethernet  connected  eth_switch
```

---

# Step 9: Test Sonar Connectivity

Ping Sonar 1:

```bash
ping -I eth0 192.168.2.90
```

Ping Sonar 2:

```bash
ping -I eth0 192.168.2.91
```

Both should respond successfully.

---
