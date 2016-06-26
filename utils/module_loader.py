#!/usr/bin/env python3

##########################
#                        #
#   TEXTSIRI NEO v1.0    #
#                        #
# Licensed under the MIT #
# license. Enjoy.        #
#                        #
##########################

# utils/module_loader.py = Module loader and the heart of TextSiri.

import imp, os, glob
import sys
from utils import logger

# Thanks to nathan0 at GitHub for this
def load_modules(dirname):
    module_list = []
    plugins_folder = [os.path.join(os.getcwd(), dirname)]
    plugins = set(glob.glob(os.path.join(dirname, "*.py")))
    for plugin in plugins:
        if plugin.find("__") != -1:
            continue
        _plugin = os.path.join(os.getcwd(), plugin)
        try:
            moduleinfo = imp.find_module(plugin.split(os.sep)[1].split(".")[0], plugins_folder)
            module_object = imp.load_source(plugin, moduleinfo[1])
        except ImportError as e:
            if str(e).startswith('No module named'):
                logger.print_error('Failed to load plugin {}: the plugin could not be found!'.format(plugin))
            else:
                logger.print_error('Failed to load plugin {}: import error {}'.format(plugin, str(e)))
        except BaseException as e:
            logger.print_error("The following error occured while importing module {}: \"{}\". Please fix the issue or contact the module author. ".format(plugin, str(e)))
            sys.exit(1)
        else:
            module_list.append(module_object)
    return module_list

def load(instance, logger, dirname):
    modulelist = load_modules(dirname)
    logger.print_info("Loading {} modules".format(len(modulelist)))
    for module in modulelist:
        try:
            modulelist[modulelist.index(module)] = module.Module(instance)
        except BaseException as e:
            continue
    for module in modulelist:
        if hasattr(module, "post_init"):
            module.post_init(modulelist)
        for method in dir(module):
            if method[:3] == "on_":
                try:
                    instance.connection.add_global_handler(method[3:], getattr(module, method))
                except Exception as e:
                    logger.print_error("Error {} occured while hooking module {}.".format(e, module.info["name"]))
    logger.print_info("Checking dependencies...")
    for module in modulelist:
        mods = [x.info["name"] for x in modulelist]
        for depend in module.info["depends"]:
            if depend not in mods:
                logger.print_error("{0} depends on {1} but {1} does not exist! Download {1} or remove {0}.".format(module.info["name"], depend))
    logger.print_info("All dependencies are included.")
