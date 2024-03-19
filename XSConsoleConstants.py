# Default NTP domains are <int>.[centos|xenserver].pool.ntp.org
CENTOS_NTP_POOL_DOMAIN = "centos.pool.ntp.org"
DEFAULT_NTP_DOMAINS = [CENTOS_NTP_POOL_DOMAIN, "xenserver.pool.ntp.org"]

NUM_DEFAULT_NTP_SERVERS = 4

DEFAULT_NTP_SERVERS = ["%d.%s" % (i, CENTOS_NTP_POOL_DOMAIN) for i in range(NUM_DEFAULT_NTP_SERVERS)]
