# Raspberry Matrix LED MAX7219 show stars of Github repo

Print number of stargazers of a Github repo on a MAX7219 matrix led connected to a Raspberry PI.

## Raspberry Pi preparation

Install system libraries
```bash
sudo apt install build-essential python3-dev python3-pip libfreetype6-dev libjpeg-dev libopenjp2-7 libtiff5
```

Install python packages
```bash
sudo pip3 install luma.led_matrix
```

Activate SPI on the RPI:

- Run `sudo raspi-config`
- Use the down arrow to select 3 "Interface Options"
- Arrow down to `P4 SPI`
- Select yes when it asks you to enable SPI
- Also select yes when it asks about automatically loading the kernel module
- Use the right arrow to select the <Finish> button
- Reboot

Check that the SPI module is well loaded
```bash
lsmod | grep -i spi
```

Output example:
```
spidev                 20480  2
spi_bcm2835            20480  0
```

GPIO pin-outs

| Board Pin | Name | Remarks     | RPi Pin | RPi Function      |
| --------- | ---- | ----------- | ------- | ----------------- |
| 1         | VCC  | +5V Power   | 2       | 5V0               |
| 2         | GND  | Ground      | 6       | GND               |
| 3         | DIN  | Data In     | 19      | GPIO 10 (MOSI)    |
| 4         | CS   | Chip Select | 24      | GPIO 8 (SPI CE0)  |
| 5         | CLK  | Clock       | 23      | GPIO 11 (SPI CLK) |

## Github Token

Github has a rate limit for non-authenticated API calls. A token is required to bypass this limit.
Create a token in your dev settings, place it in a file that can be loaded then in your env.

secrets.sh
```bash
export GITHUB_TOKEN="mysecrettoken"
```

Source the file to place the token in the environment
```bash
source secrets.sh
```

## Run

```
python3 main.py
```


## Auto start on boot

Prepare log folder
```
sudo mkdir /var/log/rpi-led
sudo chown pi:pi /var/log/rpi-led
```

Create a systemd service in `/etc/systemd/system/rpi-led.service`
```
[Unit]
Description=rpi-led
Wants=network-online.target
After=network-online.target

[Service]
Environment='STDOUT=/var/log/rpi-led/main.log'
Environment='STDERR=/var/log/rpi-led/main.err.log'
Environment='GITHUB_TOKEN=mysecrettoken'
# if proxy
#Environment='HTTP_PROXY=http://myproxy.domain.com'
#Environment='HTTPS_PROXY=http://myproxy.domain.com'
KillSignal=SIGINT
ExecStart=/usr/bin/python3 /home/pi/rpi-led-github-stars/main.py > ${STDOUT} 2> ${STDERR}
User=pi

[Install]
WantedBy=multi-user.target
```

Start and enable the service
```
sudo systemctl daemon-reload
sudo systemctl start rpi-led
sudo systemctl enable rpi-led
```