from dbaas_dnsapi.models import HOST, INSTANCE
from dbaas_dnsapi.provider import DNSAPIProvider
from dbaas_dnsapi.utils import add_dns_record
from base import BaseInstanceStep


class DNSStep(BaseInstanceStep):

    def __init__(self, instance):
        super(DNSStep, self).__init__(instance)
        self.provider = DNSAPIProvider

    def do(self):
        raise NotImplementedError

    def undo(self):
        pass


class ChangeTTL(DNSStep):

    def __unicode__(self):
        return "Changing DNS TLL to {} minutes...".format(self.minutes)

    @property
    def minutes(self):
        raise NotImplementedError

    @property
    def seconds(self):
        return self.minutes * 60

    def do(self):
        self.provider.update_database_dns_ttl(
            self.infra, self.seconds
        )


class ChangeTTLTo5Minutes(ChangeTTL):

    minutes = 5


class ChangeTTLTo3Hours(ChangeTTL):

    minutes = 180


class ChangeEndpoint(DNSStep):

    def __unicode__(self):
        return "Changing DNS endpoint..."

    def do(self):
        for instance in self.host.instances.all():
            old_instance = instance.future_instance
            DNSAPIProvider.update_database_dns_content(
                self.infra, old_instance.dns,
                old_instance.address, instance.address
            )

            instance.dns = old_instance.dns
            old_instance.dns = old_instance.address
            old_instance.save()
            instance.save()

            if self.instance.id == instance.id:
                self.instance.dns = instance.dns

        old_host = self.host.future_host
        self.host.hostname = old_host.hostname
        old_host.hostname = old_host.address

        old_host.save()
        self.host.save()

        if self.infra.endpoint and old_host.address in self.infra.endpoint:
            self.infra.endpoint = self.infra.endpoint.replace(
                old_host.address, self.host.address
            )
            self.infra.save()


class CreateDNS(DNSStep):

    def __unicode__(self):
        return "Creating DNS..."

    def do(self):
        host = self.instance.hostname
        host.hostname = add_dns_record(
            databaseinfra=self.infra,
            name=self.instance.vm_name,
            ip=host.address,
            type=HOST
        )
        host.save()

        self.instance.dns = add_dns_record(
            databaseinfra=self.infra,
            name=self.instance.vm_name,
            ip=self.instance.address,
            type=INSTANCE
        )
        self.instance.save()

        self.provider.create_database_dns_for_ip(
            databaseinfra=self.infra,
            ip=self.instance.address
        )

    def undo(self):
        self.provider.remove_databases_dns_for_ip(
            databaseinfra=self.infra,
            ip=self.instance.address
        )
