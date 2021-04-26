set -x

wget https://storage.googleapis.com/tracker-266917.appspot.com/tracker-iot.tar
tar -xvf tracker-iot.tar

rm tracker-iot.tar

sudo systemctl restart tracker.service