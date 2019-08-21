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
FogLAMP implements, through his North plugin PI_server,  Basic and Kerberos authentication, the latter is especially relevant for the integration with PI Web API using `OMF`_.

The *requirements.sh* script installs the Kerberos client to allow the integration with what in the specific terminology is called KDC (the Kerberos server).

PI-Server as the North endpoint
===============================
The OSI *Connector Relay* allows token authentication while *PI Web API* supports Basic and Kerberos.

There could be more than one configuration to allow the Kerberos authentication,
the easiest one is the Windows server on which the PI-Server is executed act as the Kerberos server also.

The Windows Active directory should be installed and properly configured for allowing the Windows server to authenticate Kerberos requests.

FogLAMP North plugin
====================
The North plugin supports the configurable option *PIServerEndpoint* for allowing to select the target among:
::
	Connector Relay
	PI Web API
	Auto Discovery

*Auto Discovery* will let the North plugin to evaluate if the provided URL is related to an either *Connector Relay* or *PI Web API* endpoint.

the *PIWebAPIAuthenticationMethod* option permits to select the desired authentication among:
::
	anonymous
	basic
	kerberos

the Kerberos authentication requires a keytab file, the *PIWebAPIKerberosKeytabFileName* option specifies the name of the file expected under the
directory:
::
	${FOGLAMP_ROOT}/data/etc/kerberos

**NOTE:**

- *A keytab is a file containing pairs of Kerberos principals and encrypted keys (which are derived from the Kerberos password). A keytab file allows to authenticate to various remote systems using Kerberos without entering a password.*


FogLAMP server configuration
============================
The server on which FogLAMP is going to be executed needs to be properly configured to allow the Kerberos authentication.

The following steps are needed:

- *IP Address resolution for the KDC*

- *Kerberos client configuration*

- *Kerberos keytab file setup*

IP Address resolution of the KDC
--------------------------------
The Kerberos server name should be resolved to the corresponding IP Address, editing the */etc/hosts* is one of the possible and the easiest way, sample row to add:
::
	192.168.1.51    pi-server.dianomic.com pi-server

try the resolution of the name using the usual *ping* command:
::
	$ ping -c 1 pi-server.dianomic.com

	PING pi-server.dianomic.com (192.168.1.51) 56(84) bytes of data.
	64 bytes from pi-server.dianomic.com (192.168.1.51): icmp_seq=1 ttl=128 time=0.317 ms
	64 bytes from pi-server.dianomic.com (192.168.1.51): icmp_seq=2 ttl=128 time=0.360 ms
	64 bytes from pi-server.dianomic.com (192.168.1.51): icmp_seq=3 ttl=128 time=0.455 ms

Kerberos client configuration
-----------------------------
The server on which FogLAMP runs act like a Kerberos client and the configuration file should be edited for allowing the proper Kerberos server identification.
The information should be added into the */etc/krb5.conf* file in the corresponding section, a sample:
::
	[libdefaults]
		default_realm = DIANOMIC.COM

	[realms]
	    DIANOMIC.COM = {
	        kdc = pi-server.dianomic.com
	        admin_server = pi-server.dianomic.com
	    }

Kerberos keytab file
--------------------
The keytab file should be generated on the Kerberos server and copied into the FogLAMP server in the directory:
::
	${FOGLAMP_ROOT}/data/etc/kerberos

The name of the file should match the value of the North plugin option *PIWebAPIKerberosKeytabFileName*, by default *piwebapi_kerberos_https.keytab*

The way the keytab file is generated depends on the type of the Kerberos server, in the case of Windows Active Directory this is an sample command:
::

	ktpass -princ HTTPS/pi-server@DIANOMIC.COM -mapuser Administrator@DIANOMIC.COM -pass FogLamp200 -crypto AES256-SHA1 -ptype KRB5_NT_PRINCIPAL -out C:\Temp\piwebapi_kerberos_https.keytab





tbd:
::
	$ ls -l ${FOGLAMP_ROOT}/data/etc/kerberos
	-rwxrwxrwx 1 foglamp foglamp  91 Jul 17 09:07 piwebapi_kerberos_https.keytab

	-rw-rw-r-- 1 foglamp foglamp 199 Aug 13 15:30 README.rst


**NOTE:**




Kerberos authentication on Raspbian/Ubuntu
==========================================


Kerberos authentication on RedHat/CentOS
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
so *requirements.sh* will eventually install this version downloading the sources directly from `curl sources`_

