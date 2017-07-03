#!/bin/sh
# Installer of healthz.

HEALTHZ_DIR="$(dirname $0)/../healthz";

echo "Installing dependencies";
if [ ! -x /usr/bin/pip ]; then
  apt-get install -y -q python-pip python-mysqldb
  sleep 4
fi

# install healthcheck dependencies
pip install -r ${HEALTHZ_DIR}/requirements.txt

echo "Copying files...";
cp -a ${HEALTHZ_DIR}/rootfs/* /

echo "Starting Healthz Service"
/etc/init.d/healthz start