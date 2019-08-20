.. |br| raw:: html

   <br />

.. Links
.. _curl homepage: https://curl.haxx.se/
.. _curl sources: https://github.com/curl/curl/releases
.. _OMF: https://omf-docs.readthedocs.io/en/v1.1/

***********************
Kerberos authentication
***********************

Introduction
============
FogLAMP implements, through his North plugin PI_server,  Basic and Kerberos authentication, these are especially relevant for the integration with PI Web API using `OMF`_.

The *requirements.sh* script installs the Kerberos client to allow the integration with what in the specific terminology is called KDC.

North plugin
============
The North plugin supports the configurable option *PIServerEndpoint* for allowing to select the target among:
::
	Connector Relay
	PI Web API
	Auto Discovery

*Auto Discovery* will let the North plugin to evaluate if the provided URL is related to an either *Connector Relay* or *PI Web API* endpoint.

the *PIWebAPIAuthenticationMethod* permits to select the desired authentination among:
::
	anonymous
	basic
	kerberos

the Kerberos authentication requires a keytab file, the *PIWebAPIKerberosKeytabFileName* option specific the name of the file expected under the
directory:
::
	${FOGLAMP_ROOT}/data/etc/kerberos

**NOTE:**
- *A keytab is a file containing pairs of Kerberos principals and encrypted keys (which are derived from the Kerberos password). A keytab file allow to authenticate to various remote systems using Kerberos without entering a password.*


FogLAMP server configuration
============================
#
# Server Ip
#
sudo bash -c "cat >> /etc/hosts" << 'EOT'
192.168.1.51    win-4m7odkb0rh2.dianomic.com win-4m7odkb0rh2
EOT


sudo cat /etc/hosts

ping -c 1 win-4m7odkb0rh2.dianomic.com

#
# Krberos client
#
sudo vi /etc/krb5.conf

[libdefaults]
    default_realm = DIANOMIC.COM

[realms]
    DIANOMIC.COM = {
        kdc = win-4m7odkb0rh2.dianomic.com
        admin_server = win-4m7odkb0rh2.dianomic.com
    }

#
#

node=c7test;\
ssh foglamp@${node} mkdir -p  /home/foglamp/Development/FogLAMP/data/etc/kerberos;\
scp /home/foglamp/Development/FogLAMP/data/etc/kerberos/piwebapi_kerberos_https.keytab foglamp@${node}:/home/foglamp/Development/FogLAMP/data/etc/kerberos


ls -l /home/foglamp/Development/FogLAMP/data/etc/kerberos




KERBEROS authentication on Raspbian/Ubuntu
==========================================


KERBEROS authentication on RedHat/CentOS
========================================

RedHat and CentOS version 7.6 provide by default an old version of curl and the related libcurl,
it moreover does not support Kerberos, output of the curl provided by RedHat:
::
	$curl -V

	curl 7.29.0 (x86_64-redhat-linux-gnu) libcurl/7.29.0 NSS/3.36 zlib/1.2.7 libidn/1.28 libssh2/1.4.3
	Protocols: dict file ftp ftps gopher http https imap imaps ldap ldaps pop3 pop3s rtsp scp sftp smtp smtps telnet tftp
	Features: AsynchDNS GSS-Negotiate IDN IPv6 Largefile NTLM NTLM_WB SSL libz unix-sockets

The *requirements.sh* evaluates if the default version, 7.29.0, is installed and in this case it will build from the sources
a defined and stable version of curl to provide Kerberos authentication and a more recent version.

At the current stage as described at `curl homepage`_, the most recent stable version is the 7.65.3, released on 19th of July 2019,
so requirements.sh will eventually install this version downloadin the sources directly from `curl sources`_

