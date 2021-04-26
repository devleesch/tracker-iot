#!/bin/bash

set -x

cd "$(dirname "$0")"

rm tracker-iot.tar

tar -c -f tracker-iot.tar *.py
tar -r -f tracker-iot.tar requirements.txt
tar -r -f tracker-iot.tar config.ini.example
tar -r -f tracker-iot.tar tracker.service
tar -r -f tracker-iot.tar update.sh

cd webapp/
ng build
cd ..

tar -r -f tracker-iot.tar webapp/dist/

gsutil cp tracker-iot.tar gs://tracker-266917.appspot.com/

rm tracker-iot.tar