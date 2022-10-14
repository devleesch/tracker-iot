#!/bin/bash

set -x

cd "$(dirname "$0")"

wget https://storage.googleapis.com/tracker-266917.appspot.com/tracker-iot.tar
tar -xvf tracker-iot.tar

sudo apt install -f python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

rm tracker-iot.tar

sudo cp tracker.service /etc/systemd/system/tracker.service
sudo systemctl daemon-reload
sudo systemctl restart tracker.service
sudo systemctl status tracker.service