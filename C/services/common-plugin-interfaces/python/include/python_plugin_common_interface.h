#ifndef _PYTHON_PLUGIN_BASE_INTERFACE_H
#define _PYTHON_PLUGIN_BASE_INTERFACE_H
/*
 * FogLAMP common plugin interface
 *
 * Copyright (c) 2019 Dianomic Systems
 *
 * Released under the Apache 2.0 Licence
 *
 * Author: Massimiliano Pinto, Amandeep Singh Arora
 */

#include <map>

using namespace std;

extern "C" {
// This is the map of Python object initialised in each 
// South, Notification, Filter  plugin interfaces
static map<string, PyObject*> *pythonModules = new map<string, PyObject *>();;

// Global variable gPluginName set by PluginInterfaceInit:
// it has a different memory address when set/read by
// PluginInterfaceInit in South, Filter or Notification
static string gPluginName;

// Common methods to all plugin interfaces
static PLUGIN_INFORMATION *plugin_info_fn();
static PLUGIN_HANDLE plugin_init_fn(ConfigCategory *);
static void plugin_reconfigure_fn(PLUGIN_HANDLE*, const std::string&);
static void plugin_shutdown_fn(PLUGIN_HANDLE);

static void logErrorMessage();

/**
 * Destructor for PythonPluginHandle
 *    - Free up owned references
 *    - Unload python 3.5 interpreter
 */
void PluginInterfaceCleanup()
{
	if (!pythonModules)
	{
		Logger::getLogger()->error("pythonModules map is NULL "
					   "in PluginInterfaceCleanup, plugin '%s'",
					   gPluginName.c_str());
	}
	else
	{
		// Look for Python module for gPluginName key
		auto it = pythonModules->find(gPluginName);
		if (it != pythonModules->end())
		{
		
			// Delete PyObject
			Py_CLEAR(it->second);
			// Remove this element
			pythonModules->erase(it);
		}

		if (pythonModules->size() == 0)
		{
			// Remove map object
			delete pythonModules;
		}
	}

	// Cleanup Python 3.5
	Py_Finalize();
}

/**
 * Returns function pointer that can be invoked to call 'plugin_info'
 * function in python plugin
 */
static void* PluginInterfaceGetInfo()
{
	return (void *) plugin_info_fn;
}

/**
 * Fill PLUGIN_INFORMATION structure from Python object
 *
 * @param pyRetVal      Python 3.5 Object (dict)
 * @return              Pointer to a new PLUGIN_INFORMATION structure
 *                              or NULL in case of errors
 */
static PLUGIN_INFORMATION *Py2C_PluginInfo(PyObject* pyRetVal)
{
	// Create returnable PLUGIN_INFORMATION structure
	PLUGIN_INFORMATION *info = new PLUGIN_INFORMATION;

	// these are borrowed references returned by PyDict_Next
	PyObject *dKey, *dValue;
	Py_ssize_t dPos = 0;

	// dKey and dValue are borrowed references
	while (PyDict_Next(pyRetVal, &dPos, &dKey, &dValue))
	{
		const char* ckey = PyUnicode_AsUTF8(dKey);
		const char* cval = PyUnicode_AsUTF8(dValue);

		char *valStr = new char [string(cval).length()+1];
		std::strcpy (valStr, cval);

		if(!strcmp(ckey, "name"))
		{
			info->name = valStr;
		}
		else if(!strcmp(ckey, "version"))
		{
			info->version = valStr;
		}
		else if(!strcmp(ckey, "mode"))
		{
			info->options = 0;
			if (!strcmp(valStr, "async"))
			{
				info->options |= SP_ASYNC;
			}
			free(valStr);
		}
		else if(!strcmp(ckey, "type"))
		{
			info->type = valStr;
		}
		else if(!strcmp(ckey, "interface"))
		{
			info->interface = valStr;
		}
		else if(!strcmp(ckey, "config"))
		{
			info->config = valStr;
		}
	}

	return info;
}

/**
 * Function to invoke 'plugin_info' function in python plugin
 */
static PLUGIN_INFORMATION *plugin_info_fn()
{
	if (!pythonModules)
	{
		Logger::getLogger()->error("pythonModules map is NULL "
					   "in plugin_info_fn, plugin '%s'",
					   gPluginName.c_str());
		return NULL;
	}

	// Look for Python module for gPluginName key
	auto it = pythonModules->find(gPluginName);
	if (it == pythonModules->end() ||
	    !it->second)
	{
		Logger::getLogger()->fatal("plugin_handle: plugin_info(): "
					   "pModule is NULL for plugin '%s'",
					   gPluginName.c_str());
		return NULL;
	}
	PyObject* pFunc; 
	PyGILState_STATE state = PyGILState_Ensure();

	// Fetch required method in loaded object
	pFunc = PyObject_GetAttrString(it->second, "plugin_info");
	if (!pFunc)
	{
		Logger::getLogger()->fatal("Cannot find method 'plugin_info' "
					   "in loaded python module '%s'",
					   gPluginName.c_str());
	}

	if (!pFunc || !PyCallable_Check(pFunc))
	{
		// Failure
		if (PyErr_Occurred())
		{       
			logErrorMessage();
		}

		Logger::getLogger()->fatal("Cannot call method 'plugin_info' "
					   "in loaded python module '%s'",
					   gPluginName.c_str());
		Py_CLEAR(pFunc);

		PyGILState_Release(state);
		return NULL;
	}

	// Call Python method passing an object
	PyObject* pReturn = PyObject_CallFunction(pFunc, NULL);

	Py_CLEAR(pFunc);

	PLUGIN_INFORMATION *info = NULL;

	// Handle returned data
	if (!pReturn)
	{
		Logger::getLogger()->error("Called python script method 'plugin_info' "
					    ": error while getting result object, plugin '%s'",
					   gPluginName.c_str());
		logErrorMessage();
		info = NULL;
	}
	else
	{
		// Parse plugin information
		info = Py2C_PluginInfo(pReturn);

		// Remove pReturn object
		Py_CLEAR(pReturn);
	}

	PyGILState_Release(state);
	if (info)
	{
		// bump interface version to atleast 2.x so that we are able to handle
		// list of readings from python plugins in plugin_poll
		if (info->interface[0] =='1' &&
		    info->interface[1] == '.')
		{
			Logger::getLogger()->info("plugin_handle: plugin_info(): "
						   "Updating interface version "
						   "from '%s' to '2.0.0', plugin '%s'",
						   info->interface,
						   gPluginName.c_str());
			delete info->interface;
			char *valStr = new char[6];
			std::strcpy(valStr, "2.0.0");
			info->interface = valStr;
		}

		Logger::getLogger()->info("plugin_handle: plugin_info(): info={name=%s, "
					   "version=%s, options=%d, type=%s, interface=%s, config=%s}",
					   info->name,
					   info->version,
					   info->options,
					   info->type,
					   info->interface,
					   info->config);
	}

	return info;
}

/**
 * Function to invoke 'plugin_init' function in python plugin
 *
 * @param    config	ConfigCategory configuration object
 * @retun		PLUGIN_HANDLE object
 */
static PLUGIN_HANDLE plugin_init_fn(ConfigCategory *config)
{

	if (!pythonModules)
	{
		Logger::getLogger()->error("pythonModules map is NULL "
					   "in plugin_init_fn, plugin '%s'",
					   gPluginName.c_str());
		return NULL;
	}

	// Look for Python module for gPluginName key
	auto it = pythonModules->find(gPluginName);
	if (it == pythonModules->end() ||
	    !it->second)
	{
		Logger::getLogger()->fatal("plugin_handle: plugin_init(): "
					   "pModule is NULLi for plugin '%s'",
					   gPluginName.c_str());
		return NULL;
	}
	PyObject* pFunc; 
	PyGILState_STATE state = PyGILState_Ensure();

	// Fetch required method in loaded object
	pFunc = PyObject_GetAttrString(it->second, "plugin_init");
	if (!pFunc)
	{
		Logger::getLogger()->fatal("Cannot find method 'plugin_init' "
					   "in loaded python module '%s'",
					   gPluginName.c_str());
	}

	if (!pFunc || !PyCallable_Check(pFunc))
	{
		// Failure
		if (PyErr_Occurred())
		{
			logErrorMessage();
		}

		Logger::getLogger()->fatal("Cannot call method 'plugin_init' "
					   "in loaded python module '%s'",
					   gPluginName.c_str());
		Py_CLEAR(pFunc);

		PyGILState_Release(state);
		return NULL;
	}

	Logger::getLogger()->debug("plugin_handle: plugin_init(): "
				   "config->itemsToJSON()='%s'",
				   config->itemsToJSON().c_str());

	// Call Python method passing an object
	PyObject* pReturn = PyObject_CallFunction(pFunc,
						  "s",
						   config->itemsToJSON().c_str());

	Py_CLEAR(pFunc);

	// Handle returned data
	if (!pReturn)
	{
		Logger::getLogger()->error("Called python script method plugin_init : "
					    "error while getting result object, plugin '%s'",
					   gPluginName.c_str());
		logErrorMessage();
	}
	else
	{
		Logger::getLogger()->debug("plugin_handle: plugin_init(): "
					   "got handle from python plugin='%p', *handle %p, plugin '%s'",
					   pReturn,
					   &pReturn,
					   gPluginName.c_str());
	}
	PyGILState_Release(state);

	return pReturn ? (PLUGIN_HANDLE) pReturn : NULL;
}

/**
 * Function to invoke 'plugin_reconfigure' function in python plugin
 *
 * @param    handle	The plugin handle from plugin_init_fn
 * @param    config	The new configuration, as string
 */
static void plugin_reconfigure_fn(PLUGIN_HANDLE* handle,
				  const std::string& config)
{
	if (!pythonModules)
	{
		Logger::getLogger()->error("pythonModules map is NULL "
					   "in plugin_reconfigure_fn, plugin '%s'",
					   gPluginName.c_str());
		return;
	}

	// Look for Python module for gPluginName key
	auto it = pythonModules->find(gPluginName);
	if (it == pythonModules->end() ||
	    !it->second)
	{
		Logger::getLogger()->fatal("plugin_handle: plugin_reconfigure(): "
					   "pModule is NULL for plugin '%s'",
					   gPluginName.c_str());
		return;
	}
	if (!handle)
	{
		Logger::getLogger()->fatal("plugin_handle: plugin_reconfigure(): "
					   "handle is NULL for plugin '%s'",
					   gPluginName.c_str());
		return;
	}
	std::mutex mtx;
	PyObject* pFunc;
	lock_guard<mutex> guard(mtx);
	PyGILState_STATE state = PyGILState_Ensure();

	Logger::getLogger()->debug("plugin_handle: plugin_reconfigure(): pModule=%p, *handle=%p, plugin '%s'",
				   it->second,
				   *handle,
				   gPluginName.c_str());

	// Fetch required method in loaded object
	pFunc = PyObject_GetAttrString(it->second, "plugin_reconfigure");
	if (!pFunc)
	{
		Logger::getLogger()->fatal("Cannot find method 'plugin_reconfigure' "
					   "in loaded python module '%s'",
					   gPluginName.c_str());
	}

	if (!pFunc || !PyCallable_Check(pFunc))
	{
		// Failure
		if (PyErr_Occurred())
		{
			logErrorMessage();
		}

		Logger::getLogger()->fatal("Cannot call method plugin_reconfigure "
					   "in loaded python module '%s'",
					   gPluginName.c_str());
		Py_CLEAR(pFunc);

		PyGILState_Release(state);
		return;
	}

	Logger::getLogger()->debug("plugin_reconfigure with %s", config.c_str());

	// Call Python method passing an object and a C string
	PyObject* pReturn = PyObject_CallFunction(pFunc,
						  "Os",
						  *handle,
						  config.c_str());

	Py_CLEAR(pFunc);

	// Handle returned data
	if (!pReturn)
	{
		Logger::getLogger()->error("Called python script method plugin_reconfigure "
					    ": error while getting result object, plugin '%s'",
					   gPluginName.c_str());
		logErrorMessage();
		//*handle = NULL; // not sure if this should be treated as unrecoverable failure on python plugin side
	}
	else
	{
		Py_CLEAR(*handle);
		*handle = pReturn;
		Logger::getLogger()->debug("plugin_handle: plugin_reconfigure(): "
					   "got updated handle from python plugin=%p, plugin '%s'",
					   *handle,
					   gPluginName.c_str());
	}

	PyGILState_Release(state);
}

/**
 * Function to log error message encountered while interfacing with
 * Python runtime
 */
static void logErrorMessage()
{
	//Get error message
	PyObject *pType, *pValue, *pTraceback;
	PyErr_Fetch(&pType, &pValue, &pTraceback);
	PyErr_NormalizeException(&pType, &pValue, &pTraceback);

	PyObject* str_exc_value = PyObject_Repr(pValue);
	PyObject* pyExcValueStr = PyUnicode_AsEncodedString(str_exc_value, "utf-8", "Error ~");
	const char* pErrorMessage = pValue ?
				    PyBytes_AsString(pyExcValueStr) :
				    "no error description.";
	Logger::getLogger()->fatal("logErrorMessage: Error '%s', plugin '%s'",
				   pErrorMessage,
				   gPluginName.c_str());

	// Reset error
	PyErr_Clear();

	// Remove references
	Py_CLEAR(pType);
	Py_CLEAR(pValue);
	Py_CLEAR(pTraceback);
	Py_CLEAR(str_exc_value);
	Py_CLEAR(pyExcValueStr);
}

/**
 * Function to invoke 'plugin_shutdown' function in python plugin
 *
 * @param    handle	The plugin handle from plugin_init_fn
 */
static void plugin_shutdown_fn(PLUGIN_HANDLE handle)
{
	if (!pythonModules)
	{
		Logger::getLogger()->error("pythonModules map is NULL "
					   "in plugin_shutdown_fn, plugin '%s'",
					   gPluginName.c_str());
		return;
	}

	// Look for Python module for gPluginName key
	auto it = pythonModules->find(gPluginName);
	if (it == pythonModules->end() ||
	    !it->second)
	{
		Logger::getLogger()->fatal("plugin_handle: plugin_shutdown(): "
					   "pModule is NULL for plugin '%s'",
					   gPluginName.c_str());
		return;
	}
	if (!handle)
	{
		Logger::getLogger()->fatal("plugin_handle: plugin_shutdown(): "
					   "handle is NULL for plugin '%s'",
					   gPluginName.c_str());
		return;
	}

	PyObject* pFunc; 
	PyGILState_STATE state = PyGILState_Ensure();

	// Fetch required method in loaded object
	pFunc = PyObject_GetAttrString(it->second, "plugin_shutdown");
	if (!pFunc)
	{
		Logger::getLogger()->fatal("Cannot find method 'plugin_shutdown' "
					   "in loaded python module '%s'",
					   gPluginName.c_str());
	}

	if (!pFunc || !PyCallable_Check(pFunc))
	{
		// Failure
		if (PyErr_Occurred())
		{
			logErrorMessage();
		}

		Logger::getLogger()->fatal("Cannot call method 'plugin_shutdown' "
					   "in loaded python module '%s'",
					   gPluginName.c_str());
		Py_CLEAR(pFunc);

		PyGILState_Release(state);
		return;
	}

	// Call Python method passing an object
	PyObject* pReturn = PyObject_CallFunction(pFunc,
						  "O",
						  handle);

	Py_CLEAR(pFunc);

        // Handle return
	if (!pReturn)
	{       
		Logger::getLogger()->error("Called python script method plugin_shutdown "
					    ": error while getting result object, plugin '%s'",
					   gPluginName.c_str());
		logErrorMessage();
	}
	PyGILState_Release(state);
}

};
#endif
