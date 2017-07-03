# percona mysql slave configuration.
class {'mysql::server':
  package_name      => 'percona-server-server-5.6',
  service_name      => 'mysql',
  config_file       => '/etc/mysql/my.cnf',
  includedir        => '/etc/mysql/conf.d',
  override_options  => {
    mysqld => {
      server-id     => 2,
      bind-address  => '0.0.0.0',
      log-error     => '/var/log/mysqld.log',
      pid-file      => '/var/run/mysqld/mysqld.pid',
    },
    mysqld_safe => {
      log-error     => '/var/log/mysqld.log',
    },
  },
  users => {
    "${mysql_root_user}@%" => {
      ensure                   => 'present',
      password_hash            => mysql_password($mysql_root_pass),
    },
  },
  grants => {
    "${mysql_root_user}@%/*.*" => {
      ensure     => 'present',
      options    => ['GRANT'],
      privileges => ['ALL'],
      table      => '*.*',
      user       => "${mysql_root_user}@%",
    },
  }
}

# import database
mysql::db { $mysql_database_name:
  user            => $mysql_user,
  password        => $mysql_pass,
  host            => '%',
  grant           => ['all'],
  # sql             => '/vagrant/dump.sql',
  import_timeout  => 900,
}