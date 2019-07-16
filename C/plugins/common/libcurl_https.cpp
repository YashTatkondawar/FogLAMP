/*
 * FogLAMP HTTPS Sender implementation using the
 * libcurl library
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
#include "libcurl_https.h"

#define VERBOSE_LOG	0

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
			m_host_port(host_port),
			m_retry_sleep_time(retry_sleep_Time),
			m_max_retry (max_retry)
{
	int ret_code;

	ret_code = curl_global_init(CURL_GLOBAL_DEFAULT);

	if (ret_code == 0)
	{
		m_sender = curl_easy_init();

		if(m_sender)
		{
			curl_easy_setopt(m_sender, CURLOPT_TIMEOUT , request_timeout);
			curl_easy_setopt(m_sender, CURLOPT_CONNECTTIMEOUT,connect_timeout);
		}
		else
		{
			Logger::getLogger()->error("curl_easy_init failed, the libcurl library cannot be initialized.");
		}
	}
	else
	{
		Logger::getLogger()->error("curl_global_init failed, the libcurl library cannot be initialized.");
	}
}

/**
 * Destructor
 */
LibcurlHttps::~LibcurlHttps()
{
	curl_easy_cleanup(m_sender);

	//# FIXME_I
	/* free the custom headers */
	//curl_slist_free_all(chunk);

	curl_global_cleanup();
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
	int http_code = 201;

	Logger::getLogger()->debug("HTTPS sendRequest : method |%s| path |%s| payload |%s|",
				   method.c_str(),
				   path.c_str(),
				   payload.c_str() );
	return http_code;
}
