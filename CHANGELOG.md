v1.2

  * Show used configuration settings in debug mode.
  * Load configuration file from the directory in which the prometheus-webhook-snmp
    command is located.
  * Automatically convert hyphens to underscores in configuration file parameters.

v1.1

  * Add support for global configuration file /etc/prometheus-webhook-snmp.conf
  * Add ability to configure systemd service via /etc/default/prometheus-webhook-snmp
  * Added python3-PyYAML as new dependency
  * python3-pysnmp needs to be at least 4.4.1

v1.0

  * Initial Debian packaging.
