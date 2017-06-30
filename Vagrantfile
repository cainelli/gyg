Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  
  config.vm.provider :virtualbox do |v|
    v.customize ["modifyvm", :id, "--memory", 3024]
  end

  # install librarian-puppet and use it to download Puppet modules
  config.vm.provision :shell, :path => 'bootstrap.sh' unless ENV['LIBRARIAN'] == 'false'
  
   # master database
  config.vm.define "master" do |master|
    config.vm.network "private_network", ip: "10.0.0.11"
    config.vm.box_check_update = false
    config.vm.hostname = "master"
    config.vm.synced_folder ".", "/vagrant"

    config.vm.provision :puppet do |puppet|
      puppet.manifests_path = "puppet/manifests"
      puppet.manifest_file = "master.pp"
      puppet.module_path = "puppet/modules"
      puppet.options = ['--verbose']
      # puppet.facter = {
      #     "pma_mysql_root_password"  => "root",
      #     "pma_controluser_password" => "awesome"
      # }
    end
  end

  # slave database
  # config.vm.define "slave" do |slave|
  #   config.vm.network "private_network", ip: "10.0.0.12"
  #   config.vm.box_check_update = false
  #   config.vm.hostname = "slave"
  #   config.vm.synced_folder ".", "/vagrant"

  #   config.vm.provision :puppet do |puppet|
  #     puppet.manifests_path = "puppet/manifests"
  #     puppet.manifest_file = "slave.pp"
  #     puppet.module_path = "puppet/modules"
  #     puppet.options = ['--verbose']
  #     puppet.facter = {
  #         "pma_mysql_root_password"  => "root",
  #         "pma_controluser_password" => "awesome"
  #     }
  #   end
  # end
end