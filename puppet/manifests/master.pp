# percona mysql master configuration.
class {'::mysql::server':
  package_name      => 'percona-server-server-5.6',
  restart           => true,
  service_name      => 'mysql',
  config_file       => '/etc/mysql/my.cnf',
  includedir        => '/etc/mysql/conf.d',
  override_options  => {
    mysqld => {
      server-id     => 1,
      log-bin       => 'mysql-bin',
      bind-address  => '0.0.0.0',
      log-error     => '/var/log/mysqld.log',
      pid-file      => '/var/run/mysqld/mysqld.pid',
    },
    mysqld_safe => {
      log-error     => '/var/log/mysqld.log',
    },
  },
  users => {
    "${mysql_replication_user}@%" => {
      ensure                   => 'present',
      password_hash            => mysql_password($mysql_replication_pass),
    },
    "${mysql_root_user}@%" => {
      ensure                   => 'present',
      password_hash            => mysql_password($mysql_root_pass),
    },
  },
  grants => {
    "${mysql_replication_user}@%/*.*" => {
      ensure     => 'present',
      options    => ['GRANT'],
      privileges => ['REPLICATION SLAVE'],
      table      => '*.*',
      user       => "${mysql_replication_user}@%",
    },
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
  grant           => ['ALL'],
  sql             => '/vagrant/dump.sql',
  import_timeout  => 900,
}