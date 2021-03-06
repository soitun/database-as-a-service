# -*- coding: utf-8 -*-
from __future__ import absolute_import
from drivers.replication_topologies.redis import RedisSentinel, RedisSingle, \
    RedisSentinelNoPersistence
from drivers.tests.test_replication_topologies import AbstractReplicationTopologySettingsTestCase


class AbstractBaseRedisTestCase(AbstractReplicationTopologySettingsTestCase):

    def _get_deploy_first_settings(self):
        return (
            'workflow.steps.redis.deploy.build_databaseinfra.BuildDatabaseInfra',
            'workflow.steps.redis.deploy.create_virtualmachines.CreateVirtualMachine',
            'workflow.steps.redis.deploy.create_dns.CreateDns',
            'workflow.steps.util.deploy.create_nfs.CreateNfs',
            'workflow.steps.redis.deploy.init_database.InitDatabaseRedis',
            'workflow.steps.util.deploy.config_backup_log.ConfigBackupLog',
            'workflow.steps.util.deploy.check_database_connection.CheckDatabaseConnection',
            'workflow.steps.util.deploy.check_dns.CheckDns',
            'workflow.steps.util.deploy.start_monit.StartMonit',
        )

    def _get_deploy_last_settings(self):
        return (
            'workflow.steps.util.deploy.build_database.BuildDatabase',
            'workflow.steps.util.deploy.check_database_binds.CheckDatabaseBinds',
        )

    def _get_clone_settings(self):
        return self._get_deploy_first_settings() + self._get_deploy_last_settings() + (
            'workflow.steps.redis.clone.clone_database.CloneDatabase',
        ) + self._get_monitoring_settings()

    def _get_resize_extra_steps(self):
        return super(AbstractBaseRedisTestCase, self)._get_resize_extra_steps() + (
            'workflow.steps.util.infra.Memory',
        )

    def _get_upgrade_steps_extra(self):
        return (
            'workflow.steps.util.plan.InitializationForUpgrade',
            'workflow.steps.util.plan.ConfigureForUpgrade',
        )


class TestRedisSingle(AbstractBaseRedisTestCase):

    def _get_replication_topology_driver(self):
        return RedisSingle()

    def _get_deploy_settings(self):
        return [{
            'Creating virtual machine': (
                'workflow.steps.util.vm.CreateVirtualMachineNewInfra',
            )}, {
            'Creating dns': (
                'workflow.steps.util.dns.CreateDNS',
            )}, {
            'Creating disk': (
                'workflow.steps.util.disk.CreateExport',
            )}, {
            'Waiting VMs': (
                'workflow.steps.util.vm.WaitingBeReady',
                'workflow.steps.util.vm.UpdateOSDescription'
            )}, {
            'Configuring database': (
                'workflow.steps.util.plan.InitializationForNewInfra',
                'workflow.steps.util.plan.ConfigureForNewInfra',
                'workflow.steps.util.database.Start',
                'workflow.steps.util.database.CheckIsUp',
                'workflow.steps.util.infra.UpdateEndpoint',
            )}, {
            'Check DNS': (
                'workflow.steps.util.dns.CheckIsReady',
            )}, {
            'Creating Database': (
                'workflow.steps.util.database.Create',
            )}, {
            'Creating monitoring and alarms': (
                'workflow.steps.util.zabbix.CreateAlarms',
                'workflow.steps.util.db_monitor.CreateInfraMonitoring',
            )
        }]

    def _get_restore_snapshot_settings(self):
        return [{
            'Disable monitoring': (
                'workflow.steps.util.zabbix.DisableAlarms',
                'workflow.steps.util.db_monitor.DisableMonitoring',
            )}, {
            'Restoring': (
                'workflow.steps.util.disk.RestoreSnapshot',
            )}, {
            'Stopping datbase': (
                'workflow.steps.util.database.Stop',
                'workflow.steps.util.database.CheckIsDown',
            )}, {
            'Configuring': (
                'workflow.steps.util.disk.AddDiskPermissionsRestoredDisk',
                'workflow.steps.util.disk.UnmountOldestExportRestore',
                'workflow.steps.util.disk.MountNewerExportRestore',
                'workflow.steps.util.disk.ConfigureFstabRestore',
                'workflow.steps.util.plan.ConfigureRestore',
            )}, {
            'Starting database': (
                'workflow.steps.util.database.Start',
                'workflow.steps.util.database.CheckIsUp',
            )}, {
            'Old data': (
                'workflow.steps.util.disk.BackupRestore',
                'workflow.steps.util.disk.UpdateRestore',
            )}, {
            'Enabling monitoring': (
                'workflow.steps.util.db_monitor.EnableMonitoring',
                'workflow.steps.util.zabbix.EnableAlarms',
            )
        }]

class TestRedisSentinel(AbstractBaseRedisTestCase):

    def _get_replication_topology_driver(self):
        return RedisSentinel()

    def _get_upgrade_steps_final(self):
        return [{
            'Resetting Sentinel': (
                'workflow.steps.redis.upgrade.sentinel.Reset',
                'workflow.steps.util.database.SetSlave',
            ),
        }] + super(TestRedisSentinel, self)._get_upgrade_steps_final()

    def _get_add_database_instances_middle_settings(self):
        return (
            'workflow.steps.util.plan.Initialization',
            'workflow.steps.util.plan.Configure',
            'workflow.steps.util.database.Start',
            'workflow.steps.redis.horizontal_elasticity.database.AddInstanceToRedisCluster',
        )

    def _get_reinstallvm_steps_final(self):
        return [{
            'Resetting Sentinel': (
                'workflow.steps.redis.upgrade.sentinel.ResetAllSentinel',
                'workflow.steps.util.database.SetSlave',
            ),
        }] + super(TestRedisSentinel, self)._get_reinstallvm_steps_final()

    def _get_deploy_settings(self):
        return [{
            'Creating virtual machine': (
                'workflow.steps.util.vm.CreateVirtualMachineNewInfra',
            )}, {
            'Creating dns': (
                'workflow.steps.util.dns.CreateDNSSentinel',
            )}, {
            'Creating disk': (
                'workflow.steps.util.disk.CreateExport',
            )}, {
            'Waiting VMs': (
                'workflow.steps.util.vm.WaitingBeReady',
                'workflow.steps.util.vm.UpdateOSDescription'
            )}, {
            'Configuring database': (
                'workflow.steps.util.plan.InitializationForNewInfraSentinel',
                'workflow.steps.util.plan.ConfigureForNewInfraSentinel',
            )}, {
            'Starting database': (
                'workflow.steps.util.database.StartSentinel',
                'workflow.steps.util.database.CheckIsUp',
            )}, {
            'Configuring sentinel': (
                'workflow.steps.redis.upgrade.sentinel.Reset',
                'workflow.steps.util.database.SetSlave'
            )}, {
            'Check DNS': (
                'workflow.steps.util.dns.CheckIsReady',
            )}, {
            'Creating Database': (
                'workflow.steps.util.database.Create',
            )}, {
            'Creating monitoring and alarms': (
                'workflow.steps.util.sentinel.CreateAlarmsNewInfra',
                'workflow.steps.util.db_monitor.CreateInfraMonitoring',
            )
        }]

    def _get_restore_snapshot_settings(self):
        return [{
            'Disable monitoring': (
                'workflow.steps.util.zabbix.DisableAlarms',
                'workflow.steps.util.db_monitor.DisableMonitoring',
            )}, {
            'Restoring': (
                'workflow.steps.util.disk.RestoreSnapshot',
            )}, {
            'Stopping datbase': (
                'workflow.steps.util.database.Stop',
                'workflow.steps.util.database.CheckIsDown',
            )}, {
            'Configuring': (
                'workflow.steps.util.disk.AddDiskPermissionsRestoredDisk',
                'workflow.steps.util.disk.UnmountOldestExportRestore',
                'workflow.steps.util.disk.MountNewerExportRestore',
                'workflow.steps.util.disk.ConfigureFstabRestore',
                'workflow.steps.util.disk.CleanData',
                'workflow.steps.util.disk.RemoveDeprecatedFiles',
                'workflow.steps.util.plan.ConfigureRestore',
            )}, {
            'Starting database': (
                'workflow.steps.util.database.Start',
                'workflow.steps.util.database.CheckIsUp',
            )}, {
            'Configuring sentinel': (
                'workflow.steps.redis.upgrade.sentinel.ResetAllSentinel',
                'workflow.steps.util.database.SetSlaveRestore',
            )}, {
            'Old data': (
                'workflow.steps.util.disk.BackupRestore',
                'workflow.steps.util.disk.UpdateRestore',
            )}, {
            'Enabling monitoring': (
                'workflow.steps.util.db_monitor.EnableMonitoring',
                'workflow.steps.util.zabbix.EnableAlarms',
            )
        }]

class AbstractBaseRedisNoPersistenceTestCase(AbstractBaseRedisTestCase):
    pass


class TestRedisSentinelNoPersistence(TestRedisSentinel):
    pass
