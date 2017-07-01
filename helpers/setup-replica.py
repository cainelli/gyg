#!/usr/bin/python
import argparse
import MySQLdb as mdb

def get_mysql_bin_seq(master_host, master_user, master_password):
  ''' This function returns the current file name and position from master.:  
    SHOW MASTER STATUS;
    +------------------+----------+--------------+------------------+-------------------+
    | File             | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set |
    +------------------+----------+--------------+------------------+-------------------+
    | mysql-bin.000024 | 10715811 |              |                  |                   |
    +------------------+----------+--------------+------------------+-------------------+

  :param: master_host: Master hostname or IP address.
  :param: master_user: Master's username with root privileges.
  :param: master_pass: username's password.
 
  :returns:arr: [file, position]
  '''
  con = mdb.connect(master_host, master_user, master_password)
  cur = con.cursor(mdb.cursors.DictCursor)
  
  cur.execute('FLUSH TABLES WITH READ LOCK')
  cur.execute('SHOW MASTER STATUS')
  r = cur.fetchone()
  
  # TODO: type checking.
  return  [r['File'], int(r['Position'])]

def set_replication(slave_host, slave_user, slave_password, master_host, rep_user, rep_password, master_log_file, master_log_pos):
  ''' This function setup the replication on the slave server.
  
  :param: slave_host: Slave Hostname or IP address to configure the replication.
  :param: slave_user: Slave's username with root privileges.
  :param: slave_password: username's password.
  :param: master_host: Master host which you want to change(CHANGE MASTER TO MASTER_HOST=....).
  :param: rep_user: Replication user with the proper role.
  :param: rep_password: replication user's password.
  :param: master_log_file: Current file from master. You can get this running `SHOW MASTER STATUS` on master or using get_mysql_bin_seq function.
  :param: master_log_pos: Current log position from master. You can get this running `SHOW MASTER STATUS` on master or using get_mysql_bin_seq function.
  '''

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

  args = parser.parse_args()
  
  try:
    # getting log bin file and its position from master.
    master_log_file, master_log_pos = get_mysql_bin_seq(master_host=args.master_host,
                                                        master_user=args.master_user,
                                                        master_password=args.master_password)


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