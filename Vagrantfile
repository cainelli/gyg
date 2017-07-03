require 'yaml'
yaml = YAML::load(File.read("#{File.dirname(__FILE__)}/config.yaml"))
configuration = yaml['configs']

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  
  config.vm.provider :virtualbox do |v|
    v.customize ["modifyvm", :id, "--memory", 3024]
  end

  # install librarian-puppet and use it to download Puppet modules
  config.vm.provision :shell, :path => 'bootstrap.sh' unless ENV['LIBRARIAN'] == 'false'
  
   # master database
  config.vm.define "master" do |master|
    master.vm.network "private_network", ip: configuration['master']['ip']
    master.vm.box_check_update = false
    master.vm.hostname = "master"
    master.vm.synced_folder ".", "/vagrant"

    master.vm.provision :puppet do |puppet|
      puppet.manifests_path = "puppet/manifests"
      puppet.manifest_file = "master.pp"
      puppet.module_path = "puppet/modules"
      puppet.options = ['--verbose']
      puppet.facter = {
        "mysql_user" => configuration['mysql_user'],
        "mysql_pass" => configuration['mysql_pass'],
        "mysql_root_user" => configuration['master']['mysql_root_user'],
        "mysql_root_pass" => configuration['master']['mysql_root_pass'],
        "mysql_replication_user" => configuration['master']['mysql_replication_user'],
        "mysql_replication_pass" => configuration['master']['mysql_replication_pass'],
        "mysql_database_name" => configuration['mysql_database_name'],
      }
    end
  end

  # slave database
  config.vm.define "slave" do |slave|
    slave.vm.network "private_network", ip: configuration['slave']['ip']
    slave.vm.box_check_update = false
    slave.vm.hostname = "slave"
    slave.vm.synced_folder ".", "/vagrant"

    slave.vm.provision :puppet do |puppet|
      puppet.manifests_path = "puppet/manifests"
      puppet.manifest_file = "slave.pp"
      puppet.module_path = "puppet/modules"
      puppet.options = ['--verbose']
      puppet.facter = {
        "mysql_user" => configuration['mysql_user'],
        "mysql_pass" => configuration['mysql_pass'],
        "mysql_root_user" => configuration['slave']['mysql_root_user'],
        "mysql_root_pass" => configuration['slave']['mysql_root_pass'],
        "mysql_database_name" => configuration['mysql_database_name'],
      }
    end

    # configure health check application.
    slave.vm.provision "shell",
        inline: "/vagrant/helpers/healthz-install.sh"
    
    # configure replica.
    slave.vm.provision "shell",
      inline: "/vagrant/helpers/setup-replica.py \
      --master-host=$1 \
      --master-user=$2 \
      --master-password=$3 \
      --slave-host=$4 \
      --slave-user=$5 \
      --slave-password=$6 \
      --replication-user=$7 \
      --replication-password=$8 \
      --database=$9",
      args: [
        configuration['master']['ip'],
        configuration['master']['mysql_root_user'],
        configuration['master']['mysql_root_pass'],
        configuration['slave']['ip'],
        configuration['slave']['mysql_root_user'],
        configuration['slave']['mysql_root_pass'],
        configuration['master']['mysql_replication_user'],
        configuration['master']['mysql_replication_pass'],
        configuration['mysql_database_name']
      ]
  end
end