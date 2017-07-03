#!/usr/bin/python
import argparse
import MySQLdb as mdb
from subprocess import Popen, PIPE

def mysql_dump(master_host, master_user, master_password, slave_host, slave_user, slave_password, database):
  """ Running this function to create dump from master and import to slave.

  Args:
    master_host (str): Master hostname or IP address.
    master_user (str): Master's username with root privileges.
    master_pass (str): username's password.
    slave_host (str): Slave Hostname or IP address to configure the replication.
    slave_user (str): Slave's username with root privileges.
    slave_password (str): username's password.

  TODO:
    - This function uses mysqldump/mysql CLI to dump the database from master to slave.
    Use MySQLdb API should be better. 
  """
  con = mdb.connect(master_host, master_user, master_password)
  cur = con.cursor(mdb.cursors.DictCursor)
  
  # locking tables.
  cur.execute('FLUSH TABLES WITH READ LOCK')
  
  print('importing database[%s] dump from master. This can take a while.' % database)
  cmd = "mysql -h %s -u %s --password=%s %s" % (slave_host, slave_user, slave_password, database)
  mysql = Popen(cmd.split(), stdin=PIPE, stdout=PIPE)

  cmd = "mysqldump -h %s -u %s --password=%s %s" % (master_host, master_user, master_password, database)
  mysqldump = Popen(cmd.split(), stdout=mysql.stdin)
  
  mysql_stdout = mysql.communicate()[0]
  mysqldump.wait()

  # unlocking tables.
  cur.execute('UNLOCK TABLES')

def get_mysql_bin_seq(master_host, master_user, master_password):
  """ This function returns the current file name and position from master.:  
    SHOW MASTER STATUS;
    +------------------+----------+--------------+------------------+-------------------+
    | File             | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set |
    +------------------+----------+--------------+------------------+-------------------+
    | mysql-bin.000024 | 10715811 |              |                  |                   |
    +------------------+----------+--------------+------------------+-------------------+

  Args:
    master_host (str): Master hostname or IP address.
    master_user (str): Master's username with root privileges.
    master_pass (str): username's password.
 
  Returns:
    Array with file(str) and its position(int):

      [file, position]
  """
  print('getting information from master...')
  con = mdb.connect(master_host, master_user, master_password)
  cur = con.cursor(mdb.cursors.DictCursor)
  
  cur.execute('SHOW MASTER STATUS')
  r = cur.fetchone()
  
  # TODO: type checking.
  return  [r['File'], int(r['Position'])]

def set_replication(slave_host, slave_user, slave_password, master_host, rep_user, rep_password, master_log_file, master_log_pos):
  """ This function setup the replication on the slave server.
  Args:
    slave_host (str): Slave Hostname or IP address to configure the replication.
    slave_user (str): Slave's username with root privileges.
    slave_password (str): username's password.
    master_host (str): Master host which you want to change(CHANGE MASTER TO MASTER_HOST=....).
    rep_user (str): Replication user with the proper role.
    rep_password (str): replication user's password.
    master_log_file (str): Current file from master. You can get this running `SHOW MASTER STATUS` on master or using get_mysql_bin_seq function.
    master_log_pos (int): Current log position from master. You can get this running `SHOW MASTER STATUS` on master or using get_mysql_bin_seq function.
  """
  print('configuring replication...')
  con = mdb.connect(slave_host, slave_user, slave_password)
  cur = con.cursor(mdb.cursors.DictCursor)
    
  cur.execute('STOP SLAVE')
  cur.execute("CHANGE MASTER TO MASTER_HOST='%s', MASTER_USER='%s', MASTER_PASSWORD='%s', MASTER_LOG_FILE='%s', MASTER_LOG_POS=%s" % (master_host, rep_user, rep_password, master_log_file, master_log_pos))
  cur.execute('START SLAVE')
  r = cur.fetchone()

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Configure MySQL Replication of a Given Master.')
  
  parser.add_argument('--master-host', dest='master_host', action='store',
                      required=True,
                      help='Master hostname or IP address.')
  
  parser.add_argument('--master-user', dest='master_user', action='store',
                      required=False, default='root',
                      help='Master\'s User.')

  parser.add_argument('--master-password', dest='master_password', action='store',
                      required=False, default='',
                      help='Master\'s Password.')
  
  parser.add_argument('--slave-user', dest='slave_user', action='store',
                      required=False, default='root',
                      help='Slave\'s User.')

  parser.add_argument('--slave-password', dest='slave_password', action='store',
                      required=False, default='',
                      help='Slave\'s Password.')
  
  parser.add_argument('--slave-host', dest='slave_host', action='store',
                      required=False, default='localhost',
                      help='Slave hostname or IP address.')

  parser.add_argument('--replication-user', dest='replication_user', action='store',
                      required=False,
                      help='Replication user.')

  parser.add_argument('--replication-password', dest='replication_password', action='store',
                      required=True,
                      help='Replication password.')

  parser.add_argument('--database', dest='database', action='store',
                      required=False,
                      help='Specify the database which the data will be copied from.')

  args = parser.parse_args()
  
  try:
    # getting log bin file and its position from master.
    master_log_file, master_log_pos = get_mysql_bin_seq(master_host=args.master_host,
                                                        master_user=args.master_user,
                                                        master_password=args.master_password)

    # import database from master.
    mysql_dump(master_host=args.master_host,
                master_user=args.master_user,
                master_password=args.master_password,
                slave_host=args.slave_host,
                slave_user=args.slave_user,
                slave_password=args.slave_password,
                database=args.database)

    # configure the replication on the slave side.
    set_replication(slave_host=args.slave_host, 
                    slave_user=args.slave_user,
                    slave_password=args.slave_password,
                    master_host=args.master_host,
                    rep_user=args.replication_user,
                    rep_password=args.replication_password,
                    master_log_file=master_log_file,
                    master_log_pos=master_log_pos)
    print('done.')
  except Exception, e:
    print('something went wrong: %s' % e)