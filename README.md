# GYG

This project creates a Percona MySQL Master x Slave cluster.

[![asciicast](https://asciinema.org/a/127612.png)](https://asciinema.org/a/127612)

# Introduction


- Master Provisioning
  - Percona MySQL 5.6 installation.
  - Percona MySQL configuration.
    - creates default `root@localhost` user NO Password.
    - creates custom root user `${mysql_root_user}@%`.
    - creates replication user $`${mysql_replication_user}@%`.
  - Import `dump.sql` dump.

- Slave Provisioning
  - Percona MySQL 5.6 installation.
  - Percona MySQL configuration.
    - creates default `root@localhost` user and ***NO Password***.
    - creates custom root user `${mysql_root_user}@%`.
  - Slave: Replication Health check.
    - Daemon start/stop script (`/etc/init.d/healthz`).
    - Basic `Slave_SQL_Running` check. `curl http://localhost:5000/healthz` (TODO: [#9](https://github.com/cainelli/gyg/issues/9)).
    - Replication setup script.
      1. Lock master's table.
      2. dumps `${mysql_database_name}` from master and load its data to slave.
      3. gets log bin file and its position from master.
      4. configure replication on slave.
      5. unlock tables from master.

# Setup

Clone this repository
```
git clone https://github.com/cainelli/gyg.git
cd gyg
```

If you want a custom mysql user/password or table to replicate you should take a look into `config.yaml`. Otherwise, you can continue with the default configuration.

```yaml
---
configs:
  mysql_database_name: gyg-selfish
  mysql_user: gyg
  mysql_pass: gyg_pass
  master:
    ip: 10.0.0.11
    mysql_root_user: gyg_root
    mysql_root_pass: gyg_pass
    mysql_replication_user: gyg_repl
    mysql_replication_user: gyg_pass
  slave:
    ip: 10.0.0.12
    mysql_root_user: gyg_root
    mysql_root_pass: gyg_pass
```

`mysql_database_name`: Database name to create and replicate.(supported one database).

`mysql_user`: MySQL username to be created with permissions to the above database.

`mysql_pass`: Password of the user above.

`ip`: The ip address used on the master and slave.

`mysql_root_user`: Custom root user. This root user has access from anywhare(`%`).

`mysql_root_pass`: Custom root user's password.

`mysql_replication_user`: User used for the replication.

`mysql_replication_user`: Replication user's password.



:warning: Make sure you have the `dump.sql`(**not compressed**) file in the project's repository before continue.

```bash
vagrant up
```
