import os
import sys
from os import path
from collections import OrderedDict
from ConfigParser import ConfigParser
import _winreg
from distutils.msvc9compiler import find_vcvarsall
import setuptools

HCU = _winreg.HKEY_CURRENT_USER


def show_compiler():
    from distutils.core import Distribution
    dist = Distribution()
    dist.parse_config_files()
    opt = dist.command_options
    try:
        fn, compiler_name = opt["build"]["compiler"]
    except:
        from distutils.ccompiler import get_default_compiler
        fn = "default"
        compiler_name = get_default_compiler()

    from distutils import ccompiler
    version = ""
    if compiler_name == "msvc":
        compiler = ccompiler.new_compiler(compiler=compiler_name)
        version = str(compiler._MSVCCompiler__version)
    print "{} {} defined by {}".format(compiler_name, version, fn)


def set_msvc_version(version):
    import sys
    import re
    from distutils import msvc9compiler
    sys.version = re.sub(r"MSC v.(\d\d\d\d)", r"MSC v.{:02d}00".format(version+6), sys.version)
    msvc9compiler.VERSION = msvc9compiler.get_build_version()


def read_config(fn):
    config = OrderedDict()
    if not path.exists(fn):
        return config
    parser = ConfigParser()
    parser.read(fn)
    for section in parser.sections():
        options_dict = OrderedDict()
        config[section] = options_dict
        options = parser.options(section)
        for option in options:
            options_dict[option] = parser.get(section, option)
    return config


def write_config(fn, config):
    with open(fn, "w") as f:
        for section, options_dict in config.items():
            f.write("[{}]\n".format(section))
            for option, value in options_dict.items():
                f.write("{}={}\n".format(option, value))
            f.write("\n")


def set_compiler(compiler):
    """
    change default compiler by modify distutils.cfg

    :param compiler: mingw32 or msvc"
    """
    from os import path
    sys_dir = path.dirname(sys.modules['distutils'].__file__)
    sys_file = path.join(sys_dir, "distutils.cfg")
    config = read_config(sys_file)
    if "build" not in config:
        config["build"] = OrderedDict()
    build_options = config["build"]
    build_options["compiler"] = compiler
    write_config(sys_file, config)


def get_vc9_dir():
    import distutils
    Reg = distutils.msvc9compiler.Reg
    VC_BASE = r'Software\%sMicrosoft\DevDiv\VCForPython\%0.1f'
    version = 9
    key = VC_BASE % ('', version)
    try:
        productdir = Reg.get_value(key, "installdir")
    except KeyError:
        try:
            key = VC_BASE % ('Wow6432Node\\', version)
            productdir = Reg.get_value(key, "installdir")
        except KeyError:
            productdir = None
    return productdir.rstrip()


def add_vc9_reg(vc_dir):
    key = _winreg.CreateKeyEx(HCU, r"Software\Microsoft\VisualStudio\9.0\Setup\VC")
    _winreg.SetValueEx(key, "ProductDir", None, _winreg.REG_SZ, vc_dir)
    bat_path = find_vcvarsall(9.0)
    if bat_path is not None and path.exists(bat_path):
        print "Succeeded"
    else:
        print "Failed"


def remove_vc9_reg():
    try:
        _winreg.DeleteKeyEx(HCU, r"Software\Microsoft\VisualStudio\9.0\Setup\VC")
        print "Removed"
    except WindowsError:
        print "key not exist"


def select_mingw32():
    set_compiler("mingw32")


def select_msvcpy():
    set_compiler("msvc")
    vc_dir = get_vc9_dir()
    if not path.exists(vc_dir):
        print vc_dir, "not exists"
        print "Please install Visual C++ for Python first"
        return
    add_vc9_reg(vc_dir)


def select_msvc(version=None):
    set_compiler("msvc")
    if version is None:
        for ver in range(20, 9, -1):
            vc_dir = find_vcvarsall(ver)
            if vc_dir is not None:
                break
        else:
            print "No Visual C++ compiler"
            return
    else:
        vc_dir = find_vcvarsall(version)
    vc_dir = path.dirname(vc_dir)
    add_vc9_reg(vc_dir)


if __name__ == '__main__':
    opt = sys.argv[1]
    if opt == "msvcpy":
        select_msvcpy()
    elif opt == "mingw32":
        select_mingw32()
    elif opt == "msvc":
        select_msvc()
    elif opt.startswith("msvc"):
        version = float(opt[4:])
        select_msvc(version=version)
    elif opt == "remove":
        remove_vc9_reg()
