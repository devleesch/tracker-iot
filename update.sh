set -x

cd "$(dirname "$0")"

wget https://storage.googleapis.com/tracker-266917.appspot.com/tracker-iot.tar
tar -xvf tracker-iot.tar

python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

rm tracker-iot.tar

sudo systemctl restart tracker.service