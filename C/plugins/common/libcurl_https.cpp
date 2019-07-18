/*
 * FogLAMP HTTPS Sender implementation using the libcurl library
 *  - https://curl.haxx.se/libcurl/
 *  - https://github.com/curl/curl
 *
 * FogLAMP uses the libcurl library to support the Kerberos authentication
 *
 * Copyright (c) 2019 Dianomic Systems
 *
 * Released under the Apache 2.0 Licence
 *
 * Author: Stefano Simonelli
 */

#include <thread>
#include <logger.h>
#include <vector>
#include <curl/curl.h>
#include <string.h>
#include <stdlib.h>
#include "libcurl_https.h"

//# FIXME_I
#define VERBOSE_LOG 0

using namespace std;

/**
 * Constructor: host:port, connect_timeout, request_timeout,
 *              retry_sleep_Time, max_retry
 */
LibcurlHttps::LibcurlHttps(const string& host_port,
			 unsigned int connect_timeout,
			 unsigned int request_timeout,
			 unsigned int retry_sleep_Time,
			 unsigned int max_retry) :
			HttpSender(),
			m_connect_timeout(connect_timeout),
			m_request_timeout(request_timeout),
			m_host_port(host_port),
			m_retry_sleep_time(retry_sleep_Time),
			m_max_retry (max_retry)
{

	if (curl_global_init(CURL_GLOBAL_DEFAULT) != 0)
	{
		Logger::getLogger()->error("libcurl_https - curl_global_init failed, the libcurl library cannot be initialized.");
	}
}

/**
 * Destructor
 */
LibcurlHttps::~LibcurlHttps()
{
	curl_global_cleanup();
}

/**
 * Avoid libcurl debug messages
 */
size_t cb_write_data(void *buffer, size_t size, size_t nmemb, void *userp)
{
	return size * nmemb;
}

/**
 * Setups the libcurl general options used in all the HTTP methods
 *
 * @param sender    libcurl handle on which the options should be configured
 * @param path      The URL path
 * @param headers   The optional headers to send
 *
 */
void LibcurlHttps::setLibCurlOptions(CURL *sender, const string& path, const vector<pair<string, string>>& headers)
{
	string httpHeader;

#if VERBOSE_LOG
	curl_easy_setopt(m_sender, CURLOPT_VERBOSE, 1L);
#else
	curl_easy_setopt(m_sender, CURLOPT_VERBOSE, 0L);
	// this workaround is needed to avoid all libcurl debug messages
	curl_easy_setopt(m_sender, CURLOPT_WRITEFUNCTION, cb_write_data);
#endif

	curl_easy_setopt(m_sender, CURLOPT_NOPROGRESS, 1L);
	curl_easy_setopt(m_sender, CURLOPT_TCP_KEEPALIVE, 1L);

	curl_easy_setopt(m_sender, CURLOPT_TIMEOUT,        m_request_timeout);
	curl_easy_setopt(m_sender, CURLOPT_CONNECTTIMEOUT, m_connect_timeout);

	// HTTP headers handling
	m_chunk = curl_slist_append(m_chunk, "User-Agent: " HTTP_SENDER_USER_AGENT);

	for (auto it = headers.begin(); it != headers.end(); ++it)
	{
		httpHeader = (*it).first + ": " + (*it).second;
		m_chunk = curl_slist_append(m_chunk, httpHeader.c_str());
	}

	// Handle basic authentication
	if (m_authMethod == "b")
	{
		// TODO : To be implemented / verified
		httpHeader = "Basic: " + m_authBasicCredentials;
		m_chunk = curl_slist_append(m_chunk, httpHeader.c_str());

		/* set user name and password for the authentication */
		//curl_easy_setopt(m_sender, CURLOPT_USERPWD, "user:pwd");
	}
	curl_easy_setopt(m_sender, CURLOPT_HTTPHEADER, m_chunk);

	// Handle Kerberos authentication
	if (m_authMethod == "k")
	{
		Logger::getLogger()->debug("Kerberos authentication - keytab file :%s: ", getenv("KRB5_CLIENT_KTNAME"));

		curl_easy_setopt(m_sender, CURLOPT_HTTPAUTH, CURLAUTH_GSSNEGOTIATE);
		// The empty user should be defined for Kerberos authentication
		curl_easy_setopt(m_sender, CURLOPT_USERPWD, ":");
	}

	// Configure libcurl
	string url = "https://" + m_host_port + path;

	curl_easy_setopt(m_sender, CURLOPT_URL, url.c_str());

	// Setup SSL
	curl_easy_setopt(m_sender, CURLOPT_USE_SSL, CURLUSESSL_ALL);
	curl_easy_setopt(m_sender, CURLOPT_SSL_VERIFYPEER, 0L);
	curl_easy_setopt(m_sender, CURLOPT_SSL_VERIFYHOST, 0L);
	curl_easy_setopt(m_sender, CURLOPT_HTTP_VERSION, (long)CURL_HTTP_VERSION_2TLS);
}

/**
 * Send data, it retries the operation m_max_retry times
 * waiting m_retry_sleep_time*2 at each attempt
 *
 * @param method    The HTTP method (GET, POST, ...)
 * @param path      The URL path
 * @param headers   The optional headers to send
 * @param payload   The optional data payload (for POST, PUT)
 * @return          The HTTP code for the cases : 1xx Informational /
 *                                                2xx Success /
 *                                                3xx Redirection
 * @throw	    BadRequest for HTTP 400 error
 *		    std::exception as generic exception for all the
 *		    cases >= 401 Client errors / 5xx Server errors
 */
int LibcurlHttps::sendRequest(const string& method,
			     const string& path,
			     const vector<pair<string, string>>& headers,
			     const string& payload)
{
	// Variables definition
	long httpCode = 0;
	string retCode;
	string response;

	bool retry = false;
	int  retry_count = 1;
	int  sleep_time = m_retry_sleep_time;

	CURLcode res;

	enum exceptionType
	{
	    none, typeBadRequest, typeException
	};

	exceptionType exception_raised;
	string exception_message;

	// Init libcurl
	m_sender = curl_easy_init();
	if(m_sender)
	{
		setLibCurlOptions(m_sender, path, headers);
	}
	else
	{
		string errorMessage = "libcurl_https - curl_easy_init failed, the libcurl library cannot be initialized.";

		Logger::getLogger()->error(errorMessage);
		throw runtime_error(errorMessage.c_str());
	}

	// Select the requested HTTP method
	if (method.compare("POST") == 0)
	{
		curl_easy_setopt(m_sender, CURLOPT_POST, 1L);

		curl_easy_setopt(m_sender, CURLOPT_POSTFIELDS,                 payload.c_str());
		curl_easy_setopt(m_sender, CURLOPT_POSTFIELDSIZE_LARGE, (long) payload.length());
	}
	else if (method.compare("GET") == 0)
	{
		// TODO : to be implemented
		Logger::getLogger()->debug("libcurl_https - method GET currently not implemented ");
	}
	else if (method.compare("PUT") == 0)
	{
		// TODO : to be implemented
		Logger::getLogger()->debug("libcurl_https - method PUT currently not implemented ");

	}
	else if (method.compare("DELETE") == 0)
	{
		// TODO : to be implemented
		Logger::getLogger()->debug("libcurl_https - method DELETE currently not implemented ");
	}

	exception_raised = none;
	httpCode = 0;

	// Execute the HTTP method
	res = curl_easy_perform(m_sender);

	curl_easy_getinfo(m_sender, CURLINFO_RESPONSE_CODE, &httpCode);

	if(res != CURLE_OK)
	{
		Logger::getLogger()->error("libcurl_https - curl_easy_perform failed :%s: ", curl_easy_strerror(res));
	}

	// Cleanup
	curl_easy_cleanup(m_sender);
	curl_slist_free_all(m_chunk);
	m_sender = NULL;
	m_chunk = NULL;

	return httpCode;
}
