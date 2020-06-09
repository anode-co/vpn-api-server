from hades import DatabaseObject
import ipaddress


class Person(DatabaseObject):
    """Person object."""

    def __str__(self):
        """Return as stirng."""
        if hasattr(self, 'id') is False:
            self.id = None
        if hasattr(self, 'name') is False:
            self.name = None
        if hasattr(self, 'age') is False:
            self.age = None
        return "Person #{}, '{}' aged {} years".format(self.id, self.name, self.age)

    def __repr__(self):
        """Represent object."""
        return self.__str__()


class CjdnsClientPublicKey(DatabaseObject):
    """Cjdns public key object."""

    def __str__(self):
        """Return as stirng."""
        if hasattr(self, 'id') is False:
            self.id = None
        if hasattr(self, 'client_public_key') is False:
            self.client_public_key = None
        return "public key #{}, '{}'".format(self.id, self.client_public_key)

    def __repr__(self):
        """Represent object."""
        return self.__str__()


class CjdnsIpAddress(DatabaseObject):
    """Cjdns ip address."""

    def __str__(self):
        """Return as stirng."""
        if hasattr(self, 'id') is False:
            self.id = None
        if hasattr(self, 'cjdns_client_public_key_id') is False:
            self.cjdns_client_public_key_id = None
        if hasattr(self, 'ip_address') is False:
            self.ip_address = None
        return "ip address #{}, pk: {} ip: {}".format(self.id, self.cjdns_client_public_key_id, self.ip_address)

    def __repr__(self):
        """Represent object."""
        return self.__str__()


class CjdnsRouteManager:
    """Cjdns Route Manager hands out IP addresses."""

    NETWORK_IPV4 = 'ipv4'
    NETWORK_IPV6 = 'ipv6'

    in_verbose_mode = False
    database_manager = None
    config = {}
    ipv4_network = {
        'range': None,
        'allocations_per_client': None,
        'network_size': None,
        'allocations': []
    }
    ipv6_network = {
        'range': None,
        'allocations_per_client': None,
        'network_size': None,
        'allocations': []
    }
    public_keys = []
    networks = {
        NETWORK_IPV4: ipv4_network,
        NETWORK_IPV6: ipv6_network,
    }

    def __init__(self, database_manager, config, in_verbose_mode=False):
        """Initialize the object."""
        self.database_manager = database_manager
        self.in_verbose_mode = in_verbose_mode
        self.say("In verbose mode")
        self.load_config(config)

    def load_config(self, config):
        """Load the config."""
        self.config = config
        if 'ip4_range' in self.config:
            self.ipv4_network['range'] = ipaddress.ip_network(self.config['ip4_range'])
            self.ipv4_network['allocations_per_client'] = self.config['ip4_allocations_per_client']
            self.ipv4_network['network_size'] = self.config['ip4_network_size']
        if 'ip6_range' in self.config:
            self.ipv6_network['range'] = ipaddress.ip_network(self.config['ip6_range'])
            self.ipv6_network['allocations_per_client'] = self.config['ip6_allocations_per_client']
            self.ipv6_network['network_size'] = self.config['ip6_network_size']

    def preload_allocations(self):
        """Load existing allocations."""
        allocated_addresses = CjdnsIpAddress.Curator.fetch(CjdnsIpAddress, self.database_manager)
        for allocated_address in allocated_addresses:
            print("allocated address: {}".format(allocated_address))
            address = ipaddress.ip_address(allocated_address.ip_address)
            if address.version == 4:
                self.ipv4_network['allocations'].append(address)
            else:
                self.ipv6_network['allocations'].append(address)

    def allocate(self, cjdns_public_key):
        """Allocate ranges."""
        print("allocating....")
        print(cjdns_public_key)
        ipv4_allocations = []
        ipv6_allocations = []
        if cjdns_public_key in self.public_keys:
            return {
                self.NETWORK_IPV4: ipv4_allocations,
                self.NETWORK_IPV6: ipv6_allocations,
            }
        if self.ipv4_network['range'] is not None:
            ipv4_allocations = self.allocate_range(cjdns_public_key, self.NETWORK_IPV4)
        if self.ipv6_network['range'] is not None:
            ipv6_allocations = self.allocate_range(cjdns_public_key, self.NETWORK_IPV6)
        allocations = {
            self.NETWORK_IPV4: ipv4_allocations,
            self.NETWORK_IPV6: ipv6_allocations,
        }
        allocation_succeeded = False
        for network in self.networks:
            if len(allocations[network]) > 0:
                allocation_succeeded = True
                break
        if allocation_succeeded is False:
            raise self.OutOfAvailableAddressesException("Out of available addresses")
        return allocations

    def allocate_range(self, cjdns_public_key, network=NETWORK_IPV6):
        """Allocate an ip address range."""
        print("allocating range....")
        print(cjdns_public_key)
        allocations = []
        print("network type: {}".format(network))
        print(self.networks)
        '''
        if cjdns_public_key in self.public_keys:
            return allocations
        '''
        print(self.networks[network])
        print(self.networks[network]['allocations_per_client'])
        desired_num_allocations = self.networks[network]['allocations_per_client']
        # TODO: figure out how to slice out a range of IPs
        # TODO: bulk save DatabaseObject
        num_allocated = 0
        for address in self.networks[network]['range']:
            if address not in self.networks[network]['allocations']:
                cjdns_ip_address = CjdnsIpAddress(self.database_manager)
                cjdns_ip_address.ip_address = str(address)
                cjdns_ip_address.cjdns_client_public_key_id = cjdns_public_key.id
                cjdns_ip_address.save()
                allocations.append(address)
                # TODO: print this information for cjdns
                num_allocated += 1
            if num_allocated >= desired_num_allocations:
                break
        self.networks[network]['allocations'] += allocations
        return allocations

    def say(self, message):
        """Debugging output."""
        if self.in_verbose_mode is True:
            self.say("[{}] {}".format(self.__class__.__name__, message))

    class OutOfAvailableAddressesException(Exception):
        """Not enough available addresses found."""

        pass
