# -*- coding: utf-8 -*-

import imp, os, glob
import sys
from ts_api.printer import *

"""
def load_modules(dirname):
    modules = []
    for importer, package_name, _ in pkgutil.iter_modules([dirname]):
        full_package_name = '%s.%s' % (dirname, package_name)
        if full_package_name not in sys.modules:
            module = importer.find_module(package_name).load_module(full_package_name)
            modules.append(module)
    return modules
"""

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
                print('[ERROR] Failed to load plugin {}: the plugin could not be found!'.format(plugin))
            else:
                print('[ERROR] Failed to load plugin {}: import error {}'.format(plugin, str(e)))
        except BaseException as e:
            print("[ERROR] The following error occured while importing module {}: \"{}\". Please fix the issue or contact the module author. ".format(plugin, str(e)))
            sys.exit(1)
        else:
            module_list.append(module_object)
    return module_list

def load_all_modules(dirname, info, config):
    modulelist = load_modules(dirname)
    print_info("Got {} modules as a list. Sampling a new instance, getting help, commands, hooks and module info...".format(len(modulelist)))
    for module in modulelist:
        try: 
            module_instance = module.Module(config, info)
        except BaseException as e:
            if hasattr(module, "BaseMod"):
                print_info("| Skipping BaseMod or incomplete module. Error is \"{}\"".format(e))
                continue
            print_info("| Skipping invalid module")
            continue
        module_info = module_instance.module_information()
        print_info("|---- Loading module {}: 1/5 Adding module information".format(module_info["about"]["module_name"]))
        info["about"][module_info["about"]["module_name"]] = module_info["about"]
        print_info("|---- Loading module {}: 2/5 Adding respond triggers".format(module_info["about"]["module_name"]))
        info["about"][module_info["about"]["module_name"]]["triggers"] = []
        for command in module_info["triggers"]:
            info["about"][module_info["about"]["module_name"]]["triggers"].append(command)
            info["triggers"][command] = module_info["about"]["module_name"]
        print_info("|---- Loading module {}: 3/5 Adding command help".format(module_info["about"]["module_name"]))
        for command in module_info["command_help"].keys():
            print_info("| |---- Adding help for {}".format(command))
            info["command_help"][command] = module_info["command_help"][command]
        print_info("|---- Loading module {}: 4/5 Adding hooks".format(module_info["about"]["module_name"]))
        for hook in module_info["hooks"]:
            info["hooks"][hook].append(module_info["about"]["module_name"])
        print_info("|---- Loading module {}: 5/5 Inserting module instance for access".format(module_info["about"]["module_name"]))
        info["about"][module_info["about"]["module_name"]]["instance"] = module_instance
    print_info("Checking dependencies...")
    for module in info["about"].keys():
        for dependency in info["about"][module]["dependencies"]:
            if dependency not in info["about"]:
                print_fatal("Module {} was not found, which is a dependency for {}! Please download and include the required module, or remove the module that requires it. Quitting.".format(dependency, module))
                sys.exit(2)
    print_info("All dependencies are included.")
