# VPN Authorization API Server

This is a small http server and sqlite3 database that creates an API endpoint for the Anode VPN servers. 

This API endpoint accepts incoming requests from clients to authorize their cjdns public key locally, reserve IP addresses for the client, and bind the client's Internet IP address to the cjdns IP addresses for VPN routing.

## Installation

Install using GitHub

```code
# download source
git clone http://github.com/anode-co/vpn-api-server.git
cd vpn-api-server.git

# install dependencies
pip3 install -r requirements.txt

git clone http://github.com/backupbrain/hades.git
git clone http://github.com/backupbrain/simplecgi.git
git clone http://github.com/backupbrain/simplerestapi.git
```

### Configuration

Configuration is done using a [YAML](https://yaml.org/) file, which resembles this:

```yaml
cjdns:
  ip4_range: 10.66.6.0/24
  ip4_allocations_per_client: 32  # ip4_range prefix (24) to 32
  ip4_network_size: 0  # number between 0 and ip4_allocation_per_client
  ip6_range: 2c0f:f930:0002::/48
  ip6_allocations_per_client: 64  # ip6_range prefix (48) to 128
  ip6_network_size: 0  # 0 to ip6_allocation_per_client
api_server:
  port: 8888
```

The default config file is `config.yaml` in the root directory.

## Running

Run the server locally with the following command:

```code
./run_server.py
```

By default, `./config.yaml` is loaded for configuration, however you can specify another configuration file using the `-c` argument:

```code
./run_server.py -c alternate_config.yaml
```

## Known issues

* Database is no created on startup. Must use existing database.

* Currently no cjdns configuration is implemented. Authorization requests are not reflected in the cjdns route configuration.

* Currently the `ip4_allocations_per_client` and `ip6_allocations_per_client` is read as an integer, so that `ip4_allocations_per_client: 4` results is 4 IP addresses being issued to the client.

* Must run on port 8888 as clients expect VPN to be available on that port.
