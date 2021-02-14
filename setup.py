import os
import re
import sys
import fnmatch
from os.path import join
from distutils import sysconfig
from setuptools import find_packages, setup

try:
    from Cython.Distutils import build_ext
    from Cython.Distutils.extension import Extension
    cmd_class = {'build_ext': build_ext}
    cython_args = {'cython_compile_time_env': {"PY3": sys.version_info.major >= 3}}
except ImportError:
    from setuptools import Extension
    print('Cython does not appear to be installed.  Attempting to use pre-made cpp file...')
    cmd_class = {}
    cython_args = {}
    SOURCES = [s.replace(".pyx", ".c") for s in SOURCES]


# package_data depending on system

def generate_extension():
    extra_compile_args = []
    extra_link_args = []
    define_macros = []
    libs = []
    if sys.platform.startswith('linux'):
        libs.append('dl')
        # extra_compile_args.append('-DCYTHON_TRACE=1')
    elif sys.platform.startswith('darwin'):
        # libs.append('dl')
        cfg = sysconfig.get_config_vars()
        cfg['LDSHARED'] = cfg['LDSHARED'].replace('-bundle', '-dynamiclib')
        pass
    else:
        print('Sorry, your platform is not supported.')
        sys.exit(1)
    SOURCES = [
        'src/pyFlexBison/cython/core.pyx',
    ]
    return Extension(
        'pyFlexBison.libcore_',
        sources=SOURCES,
        extra_compile_args=extra_compile_args,
        libraries=libs,
        extra_link_args=extra_link_args,
        **cython_args
    )

packages = find_packages(where="src")
packages = [i for i in packages if not i.startswith("pyFlexExample")]

setup(
    name='pyLALR1',
    description='',
    # author=find_meta("author"),
    # maintainer=find_meta("maintainer"),
    # license=find_meta("license"),
    # url=find_meta("uri"),
    version='0.1',
    # keywords=KEYWORDS,
    # long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=packages,
    package_data={'pyLALR1': []},
    package_dir={
        "": "src",
    },
    zip_safe=False,
    # classifiers=CLASSIFIERS,
    install_requires=[
        "six",
        "setuptools"
    ],
    setup_requires=[
        'Cython'
    ],
    # from old setup
    cmdclass=cmd_class,
    ext_modules=[
        generate_extension()
    ]
    # py_modules=PY_MODULES,
    # scripts=SCRIPTS,
)
