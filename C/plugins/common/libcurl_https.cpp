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
#include <string.h>
#include <stdlib.h>
#include "libcurl_https.h"

//# FIXME_I
#define VERBOSE_LO 0

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

// Handles payload using the libcurl structures
struct WriteThis {
    const char *readptr;
    size_t      sizeleft;
};

// Callback for libcurl
static size_t cb_read_data(void *dest, size_t size, size_t nmemb, void *userp)
{
	struct WriteThis *wt = (struct WriteThis *)userp;
	size_t buffer_size = size*nmemb;

	// # FIXME_I
	Logger::getLogger()->debug("DBG - cb_read_data - size :%ld: nmemb :%ld: message :%s:", size, nmemb, wt->readptr);


	if(wt->sizeleft) {
		/* copy as much as possible from the source to the destination */
		size_t copy_this_much = wt->sizeleft;
		if(copy_this_much > buffer_size)
			copy_this_much = buffer_size;
		memcpy(dest, wt->readptr, copy_this_much);

		wt->readptr += copy_this_much;
		wt->sizeleft -= copy_this_much;
		return copy_this_much; /* we copied this many bytes */
	}

	return 0; /* no more data left to deliver */
}

//# FIXME_I
string g_payload;

// Callback for libcurl
static int cb_seek(void *userp, curl_off_t offset, int origin)
{
	struct WriteThis *wt = (struct WriteThis *)userp;

	wt->readptr = g_payload.c_str();
	wt->sizeleft =g_payload.length();

	// # FIXME_I
	Logger::getLogger()->debug("DBG - cb_seek - offset :%ld: origin :%ld: message :%s:", offset, origin, wt->readptr);

	return CURL_SEEKFUNC_OK;
}

// Avoid libcurl debug messages
size_t cb_write_data(void *buffer, size_t size, size_t nmemb, void *userp)
{
	return size * nmemb;
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
	string httpHeader;
	string retCode;
	string response;

	string keytabFile;
	string env;

	bool retry = false;
	int  retry_count = 1;
	int  sleep_time = m_retry_sleep_time;

	CURLcode res;

	// Handles payload using the libcurl structures
	struct WriteThis wt;
	wt.readptr = payload.c_str();
	wt.sizeleft = payload.length();

	//# FIXME_I
	g_payload = payload;

	enum exceptionType
	{
	    none, typeBadRequest, typeException
	};

	exceptionType exception_raised;
	string exception_message;


	// Code

	// Init libcurl
	m_sender = curl_easy_init();
	if(m_sender)
	{
		curl_easy_setopt(m_sender, CURLOPT_TIMEOUT , m_request_timeout);
		curl_easy_setopt(m_sender, CURLOPT_CONNECTTIMEOUT,m_connect_timeout);

		// HTTP headers handling
		m_chunk = NULL;
	}
	else
	{
		string errorMessage = "libcurl_https - curl_easy_init failed, the libcurl library cannot be initialized.";

		Logger::getLogger()->error(errorMessage);
		throw runtime_error(errorMessage.c_str());
	}

#if VERBOSE_LOG
	curl_easy_setopt(m_sender, CURLOPT_VERBOSE, 1L);
#else
	curl_easy_setopt(m_sender, CURLOPT_VERBOSE, 0L);
	// to avoid all debug messages
	curl_easy_setopt(m_sender, CURLOPT_WRITEFUNCTION, cb_write_data);
#endif

	// Handle HTTP headers
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


	// Configure libcurl
	string url = "https://" + m_host_port + path;

	curl_easy_setopt(m_sender, CURLOPT_URL, url.c_str());

	//# FIXME_I
	Logger::getLogger()->debug("libcurl_https - url :%s: ", url.c_str());

	/* require use of SSL for this, or fail */
	curl_easy_setopt(m_sender, CURLOPT_USE_SSL, CURLUSESSL_ALL);
	curl_easy_setopt(m_sender, CURLOPT_SSL_VERIFYPEER, 0L);
	curl_easy_setopt(m_sender, CURLOPT_SSL_VERIFYHOST, 0L);
	curl_easy_setopt(m_sender, CURLOPT_HTTP_VERSION, (long)CURL_HTTP_VERSION_2TLS);

	curl_easy_setopt(m_sender, CURLOPT_NOPROGRESS, 1L);
	curl_easy_setopt(m_sender, CURLOPT_TCP_KEEPALIVE, 1L);

	/* Select the requested HTTP method */
	if (method.compare("POST") == 0)
	{
		curl_easy_setopt(m_sender, CURLOPT_POST, 1L);

		//# FIXME_I
		//curl_easy_setopt(m_sender, CURLOPT_POSTFIELDS, "[    {        \"id\": \"TankMeasurement\",        \"version\": \"1.0.0.0\",        \"type\": \"object\",        \"classification\": \"dynamic\",        \"properties\": {            \"Time\": {                \"format\": \"date-time\",                \"type\": \"string\",                \"isindex\": true            },            \"Pressure\": {                \"type\": \"number\",                \"name\": \"Tank Pressure\",                \"description\": \"Tank Pressure in Pa\"            },            \"Temperature\": {                \"type\": \"number\",                \"name\": \"Tank Temperature\",                \"description\": \"Tank Temperature in K\"            }        }    } ]");
		//curl_easy_setopt(m_sender, CURLOPT_POSTFIELDSIZE_LARGE, (curl_off_t)639);
		curl_easy_setopt(m_sender, CURLOPT_POSTFIELDSIZE, (long) wt.sizeleft);

		// Configures callbacks if the method requires a payload handling
		curl_easy_setopt(m_sender, CURLOPT_READFUNCTION, cb_read_data);

		/* pointer to pass to our read function */
		curl_easy_setopt(m_sender, CURLOPT_READDATA, &wt);

		//# FIXME_I
		curl_easy_setopt(m_sender, CURLOPT_SEEKFUNCTION, cb_seek);
		curl_easy_setopt(m_sender, CURLOPT_SEEKDATA, &wt);
	}

	// Handle Kerberos authentication
	if (m_authMethod == "k")
	{
		//# FIXME_I
		keytabFile = "/home/foglamp/tmp/kerberos_https.keytab";
		//keytabFile = "/home/foglamp/tmp/kerberos_https2.keytab";
		env = "KRB5_CLIENT_KTNAME=" + keytabFile;

		putenv((char *) env.c_str());

		Logger::getLogger()->debug("Kerberos authentication - keytab file :%s: ", env.c_str());

		curl_easy_setopt(m_sender, CURLOPT_HTTPAUTH, CURLAUTH_GSSNEGOTIATE);
		// The empty user should be defined for Kerberos authentication
		curl_easy_setopt(m_sender, CURLOPT_USERPWD, ":");
	}

	// TODO : post fields handling
	//curl_easy_setopt(curl, CURLOPT_POSTFIELDS, post_fields);

	exception_raised = none;
	httpCode = 0;

	/* Now run off and do what you've been told! */
	res = curl_easy_perform(m_sender);

	curl_easy_getinfo(m_sender, CURLINFO_RESPONSE_CODE, &httpCode);

	if(res != CURLE_OK)
	{
		Logger::getLogger()->error("libcurl_https - curl_easy_perform failed :%s: ", curl_easy_strerror(res));
	}

	/* always cleanup */
	curl_easy_cleanup(m_sender);

	/* free the custom headers */
	curl_slist_free_all(m_chunk);
	m_sender = NULL;
	m_chunk = NULL;

	return httpCode;
}
