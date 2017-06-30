#!/bin/sh
# Basic bootstrap script that installs librarian-puppet and uses it to fetch
# Puppet modules. 
if [ ! -x /usr/bin/git ]; then
  apt-get install -y -q git
  sleep 4
fi

if [ "$(gem query -i -n librarian-puppet)" != "true" ]; then
  gem install --no-rdoc --no-ri librarian-puppet
  cd /vagrant/puppet && librarian-puppet install --clean --verbose
else
  cd /vagrant/puppet && librarian-puppet update --verbose
fi

# Fetch the repository packages from Percona web:
wget -c https://repo.percona.com/apt/percona-release_0.1-4.$(lsb_release -sc)_all.deb

# Install the downloaded package with dpkg. To do that, run the following commands as root or with sudo:
dpkg -i percona-release_0.1-4.$(lsb_release -sc)_all.deb

# update the local cache
apt-get update