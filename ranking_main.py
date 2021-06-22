import datetime
import time
from threading import Thread

from paramiko import SSHClient, AutoAddPolicy

import logging.handlers
logger = logging.getLogger("Snapshot")
logger.setLevel(logging.DEBUG)

my_handler = logging.handlers.RotatingFileHandler("snapshot.log", mode='w',
                                                  maxBytes=20 * 1024 * 1024,
                                                  backupCount=3,
                                                  encoding="UTF-8", delay=0)
formatter = logging.Formatter('%(asctime)s-File %(pathname)s-Line %(lineno)d-Method %(funcName)s-LogLevel'
                              ' %(levelname)s :::::: %(message)s')
my_handler.setFormatter(formatter)
logger.addHandler(my_handler)

is_zipped = False


class CheckTime(Thread):
    def __init__(self):
        super().__init__()
        self.alarm_time = "12:25:00.000000"
        self.backup = OrientdbBackup()

    # check time
    def run(self):

        while True:
            rn = str(datetime.datetime.now().time())
            logger.info(rn)
            if rn >= self.alarm_time:

                pid, status, err = self.backup.find_pid()
                if pid == '' and status == 1 and err == '':
                    report_str = f"it is  {rn} but Orientdb is still down !!!!"
                    logger.info("@armita_mani  @DehghanHossein", report_str)
                    time.sleep(300)
                elif pid.isnumeric() and is_zipped:
                    break
            time.sleep(20)


class OrientdbBackup(Thread):

    def __init__(self):
        super().__init__()
        self.ip = '172.20.20.118'
        self.username = 'root'
        self.password = 'datak!123'
        self.port = 10916
        self.database_path = '/home/orientdb/orientdb_B/databases'
        self.run_orientdb_command = 'cd /home/orientdb/orientdb_B;./bin/server.sh'
        self.nfs_address = '/home/orientdb_backups'
        self.number_of_kept_snapshot = 3
        self.client = self.create_connection()


    # create connection
    def create_connection(self):
        client = SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(self.ip, username=self.username, password=self.password, port=self.port)
        return client

    # find PID
    def find_pid(self):
        stdin, stdout, stderr = self.client.exec_command('pgrep -f  orientdb')
        err = stderr.read().decode("utf8")
        status = stdout.channel.recv_exit_status()
        pid = str(stdout.read().decode("utf8")).strip('\n')
        return pid, status, err

    # shutdown Orientdb
    def shutdown_orientdb(self, pid):
        stdin, stdout, stderr = self.client.exec_command(f'kill {pid}')
        err = stderr.read().decode("utf8")
        status = stdout.channel.recv_exit_status()
        pid, status_pid, err_pid = self.find_pid()
        if err == '' and status == 0 and pid.isnumeric() == False:
            return 'success'
        else:
            logger.error(f'Error: {err} \n status : {status}\n')
            return 'failed'

    def zip_database(self):
        # current date and time
        global is_zipped
        now = datetime.datetime.now()
        timestamp = int(datetime.datetime.timestamp(now))
        self.backup_filename = f'orientdb_backup_{timestamp}.zip'

        stdin, stdout, stderr = self.client.exec_command(
            f'cd /home ; zip -r {self.backup_filename}  {self.database_path} ')
        err = stderr.read().decode("utf8")
        status = stdout.channel.recv_exit_status()
        if err == '' and status == 0:
            is_zipped=True
            return 'success'
        else:
            logger.error(f'Error: {err} \n status : {status}\n')
            return 'failed'

    # move backup to backup folder
    def move_backup(self):
        # create sha file for zip file
        stdin_, stdout_, stderr_ = self.client.exec_command(
            f'cd /home; sha512sum {self.backup_filename} > {self.backup_filename}_sha')
        stdin, stdout, stderr = self.client.exec_command(
            f'cp /home/{self.backup_filename}_sha {self.nfs_address}; cp /home/{self.backup_filename} {self.nfs_address}')
        err = stderr.read().decode("utf8")
        status = stdout.channel.recv_exit_status()

        if err == '' and status == 0:
            logger.info(f'checking sha ...')
            sha_status = self.sha_check()
            if sha_status == 'success':
                logger.info("removing zip file in home directory")
                self.delete_file(f'/home/{self.backup_filename}_sha')
                self.delete_file(f'/home/{self.backup_filename}')
                return 'success'
        else:
            logger.info(f'Error: {err} \n status : {status}\n')
            return 'failed'

    # checking sha
    def sha_check(self):

        stdin, stdout, stderr = self.client.exec_command(
            f'chmod 777 {self.nfs_address}/{self.backup_filename}_sha;  cd {self.nfs_address};  sha512sum -c {self.backup_filename}_sha')
        err = stderr.read().decode("utf8")
        status = stdout.channel.recv_exit_status()

        if err == '' and status == 0:
            return 'success'
        else:
            logger.error(f'Error: {err} \n status : {status}\n')
            return 'failed'

    # delete snapshot
    def delete_file(self, delete_file_name):

        stdin, stdout, stderr = self.client.exec_command(f' rm -rf {delete_file_name}')
        err = stderr.read().decode("utf8")
        status = stdout.channel.recv_exit_status()

        if err == '' and status == 0:
            return 'success'
        else:
            logger.error(f'Error: {err} \n status : {status}\n')
            return 'failed'

    # run Orientdb again
    def turn_on_orientdb(self):

        stdin, stdout, stderr = self.client.exec_command(self.run_orientdb_command)
        pid, status_pid, err_pid = self.find_pid()
        if pid.isnumeric():
            return 'success', pid
        else:
            return 'failed', None

    def delete_old_snapshot(self, prefix='orientdb_backup_', postfix='.zip\n'):

        # check available snapshots
        snapshots_list = {}
        sorted_snapshots_list = {}
        delete_list = []
        stdin, stdout, stderr = self.client.exec_command(f' cd {self.nfs_address} ;  ls ')
        err = stderr.read().decode("utf8")
        status = stdout.channel.recv_exit_status()
        files = stdout.readlines()

        for file in files:
            if file.endswith(postfix):
                name = str(file).replace(postfix, '')
                snapshot_time = str(name).replace(prefix, '')
                snapshots_list[snapshot_time] = {'snapshot_time': snapshot_time, 'name': f'{name}.zip'}

        tmp = sorted(snapshots_list)
        snapshots_dates = []
        for k in tmp:
            sorted_snapshots_list[k] = snapshots_list[k]
            snapshots_dates.append(k)

        # adding expired snapshots to delete list
        if len(sorted_snapshots_list) > self.number_of_kept_snapshot:
            delete_snapshot_based_on_date = snapshots_dates[
                                            0:len(sorted_snapshots_list) - self.number_of_kept_snapshot]
            for i in delete_snapshot_based_on_date:
                delete_list.append(sorted_snapshots_list[i]['name'])
            for file in files:
                if file.endswith('_sha\n'):
                    name = str(file).replace('\n', '')
                    delete_list.append(name)

        # delete snapshots
        for item in delete_list:
            status = self.delete_file(f'{self.nfs_address}/{item}')
            if status == 'success':
                logger.info(f' {item }  is successfully deleted....')
            else:
                logger.info(f'deleting {item} failed !!!!')

        # remove zip file in /home directory

    def run(self):

        # find PID
        logger.info('finding PID ....')
        pid, status, err = self.find_pid()
        if pid == '' and status == 1 and err == '':
            logger.info('Orientdb is not UP now!!!!')
        else:
            # shutdown Orientdb
            logger.info(f'Orientdb\'s current PID is : {pid}')
            logger.info(f'shutting down Orientdb ...')
            status = self.shutdown_orientdb(pid)
            if status == 'success':
                logger.info(f'Orientdb shut downed successfully....')
            else:
                logger.info(f'Orientdb failed to shut down and backup failed!!!!')
                exit(1)

        # zip database
        logger.info(f'zipping database ....')
        status = self.zip_database()
        if status == 'success':
            logger.info(f'database is zipped successfully....')
        else:
            logger.info(f'zipping the database failed !!!!')
            logger.info(f'backup process failed !!!!')

        # run Orientdb again
        status, pid = self.turn_on_orientdb()
        if status == 'success':
            logger.info(f'Orientdb is UP successfully with pid {pid}....\n')

        else:
            logger.info(f'runnig Orientdb failed !!!!')

        # move backup file to backup directory
        status = self.move_backup()
        if status == 'success':
            logger.info(f'database is successfully backed up....')
        else:
            logger.error(f'backing up the database failed !!!!')
            exit(1)

        # remove extra backups
            logger.info(f'deleting old snapshots....')
        self.delete_old_snapshot()
        self.client.close()


if __name__ == '__main__':
    OrientdbBackup().start()
    CheckTime().start()
