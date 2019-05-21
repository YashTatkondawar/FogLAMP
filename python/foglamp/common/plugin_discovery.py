# -*- coding: utf-8 -*-

# FOGLAMP_BEGIN
# See: http://foglamp.readthedocs.io/
# FOGLAMP_END

"""Common Plugin Discovery Class"""

import os


from foglamp.common import logger
from foglamp.services.core.api import utils

__author__ = "Amarendra K Sinha, Ashish Jabble"
__copyright__ = "Copyright (c) 2017 OSIsoft, LLC"
__license__ = "Apache 2.0"
__version__ = "${VERSION}"


_logger = logger.setup(__name__)


class PluginDiscovery(object):
    def __init__(self):
        pass

    @classmethod
    def get_plugins_installed(cls, plugin_type=None, is_config=False):
        if plugin_type is None:
            plugins_list = []
            plugins_list_north = cls.fetch_plugins_installed("north", is_config)
            plugins_list_south = cls.fetch_plugins_installed("south", is_config)
            plugins_list_c_north = cls.fetch_c_plugins_installed("north", is_config)
            plugins_list_c_south = cls.fetch_c_plugins_installed("south", is_config)
            plugins_list_c_filter = cls.fetch_c_plugins_installed("filter", is_config)
            plugins_list_c_notify = cls.fetch_c_plugins_installed("notificationDelivery", is_config)
            plugins_list_c_rule = cls.fetch_c_plugins_installed("notificationRule", is_config)
            plugins_list.extend(plugins_list_north)
            plugins_list.extend(plugins_list_c_north)
            plugins_list.extend(plugins_list_south)
            plugins_list.extend(plugins_list_c_south)
            plugins_list.extend(plugins_list_c_filter)
            plugins_list.extend(plugins_list_c_notify)
            plugins_list.extend(plugins_list_c_rule)
        elif plugin_type in ['filter', 'notificationDelivery', 'notificationRule']:
            plugins_list = cls.fetch_c_plugins_installed(plugin_type, is_config)
        else:
            plugins_list = cls.fetch_plugins_installed(plugin_type, is_config)
            plugins_list.extend(cls.fetch_c_plugins_installed(plugin_type, is_config))
        return plugins_list

    @classmethod
    def fetch_plugins_installed(cls, plugin_type, is_config):
        directories = cls.get_plugin_folders(plugin_type)
        configs = []
        for d in directories:
            plugin_config = cls.get_plugin_config(d, plugin_type, is_config)
            if plugin_config is not None:
                configs.append(plugin_config)
        return configs

    @classmethod
    def get_plugin_folders(cls, plugin_type):
        dir_name = utils._FOGLAMP_ROOT + "/python/foglamp/plugins/" + plugin_type
        dir_path = []
        if utils._FOGLAMP_PLUGIN_PATH:
            plugin_paths = utils._FOGLAMP_PLUGIN_PATH.split(";")
            for pp in plugin_paths:
                if not os.path.isdir(pp):
                    _logger.warning("{} is not a directory!".format(pp))
                else:
                    subdirs = [dirs for rt, dirs, files in os.walk(pp)]
                    if not len(subdirs):
                        _logger.warning("{} - no sub directories found".format(pp))
                    else:
                        dir_path.append(any(elem in [plugin_type] for elem in subdirs[0]))

        try:
            directories = [dir_name + '/' + d for d in os.listdir(dir_name) if os.path.isdir(dir_name + "/" + d) and
                           not d.startswith("__") and d != "empty" and d != "common"]
            if len(dir_path):
                temp_list = []
                for fp in dir_path:
                    for root, dirs, files in os.walk(fp + "/" + plugin_type):
                        for name in dirs:
                            if not name.startswith("__"):
                                p = os.path.join(root, name)
                                temp_list.append(p)
                directories += temp_list
        except FileNotFoundError:
            pass
        else:
            return directories

    @classmethod
    def fetch_c_plugins_installed(cls, plugin_type, is_config):
        libs = utils.find_c_plugin_libs(plugin_type)
        configs = []
        for l in libs:
            try:
                jdoc = utils.get_plugin_info(l, dir=plugin_type)
                if bool(jdoc):
                    plugin_config = {'name': l,
                                     'type': plugin_type,
                                     'description': jdoc['config']['plugin']['description'],
                                     'version': jdoc['version']
                                     }
                    if is_config:
                        plugin_config.update({'config': jdoc['config']})
                    configs.append(plugin_config)
            except Exception as ex:
                _logger.exception(ex)

        return configs

    @classmethod
    def get_plugin_config(cls, plugin_dir, plugin_type, is_config):
        plugin_module_path = plugin_dir
        plugin_config = None

        # Now load the plugin to fetch its configuration
        try:
            plugin_info = utils.load_and_fetch_python_plugin_info(plugin_module_path,
                                                                  plugin_module_path.split('/')[-1], plugin_type)
            plugin_config = {
                'name': plugin_info['config']['plugin']['default'],
                'type': plugin_info['type'],
                'description': plugin_info['config']['plugin']['description'],
                'version': plugin_info['version']
            }
            if is_config:
                plugin_config.update({'config': plugin_info['config']})
        except TypeError as e:
            _logger.error("Plugin {} is discarded due to invalid type".format(plugin_dir))
        except FileNotFoundError as ex:
            _logger.error('Plugin "{}" import problem from path "{}". {}'.format(plugin_dir, plugin_module_path, str(ex)))
        except Exception as ex:
            _logger.exception('Plugin "{}" raised exception "{}" while fetching config'.format(plugin_dir, str(ex)))

        return plugin_config
