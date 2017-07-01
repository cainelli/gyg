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
}

# import database
mysql::db { 'gyg-selfish':
  user            => $mysql_root_user,
  password        => $mysql_root_pass,
  host            => 'localhost',
  sql             => '/vagrant/dump.sql',
  import_timeout  => 900,
}