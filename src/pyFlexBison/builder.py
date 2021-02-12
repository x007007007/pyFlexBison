from .gen_bison import BisonGenerator
from .gen_flex import FlexGenerator
from .generator import CommandGeneratorBase
import typing
import re
import sys
import warnings
from distutils import ccompiler
import os
from distutils.core import Extension
from distutils.command import build_ext
from distutils import sysconfig


class Builder(CommandGeneratorBase):
    MAC_GCC_PATH = "/usr/bin/gcc"
    bin_path: str = None
    gcc_version: typing.Tuple[int, int, int]

    include_dirs = None
    libraries = None

    def __init__(
        self,
        name: str,
        flex_generator: FlexGenerator,
        bison_generator: BisonGenerator,
        *args,
        **kwargs
    ):
        super(Builder, self).__init__(*args, **kwargs)
        self.name = name
        self.flex = flex_generator
        self.bison = bison_generator
        self.include_dirs = ['./build/']
        self.libraries = []


    def env_checker(self):
        if self.run_env is None:
            self.run_env = dict()
        if sys.platform.startswith('darwin'):
            if os.path.exists(self.MAC_GCC_PATH):
                proc = self.run_cmd([self.MAC_GCC_PATH, '--version'], self.run_env)
                res, res_err = proc.communicate()
                res = res.decode(sys.getdefaultencoding())
                match_res = re.match(r'version.*?\s*(\d+)\.(\d+)\.(\d+)', res)
                if match_res:
                    main, major, minor = (int(i) for i in match_res.groups())
                    self.gcc_version = (main, major, minor)
                    if main < 11 or (main == 11 and major < 0 ):
                        warnings.warn(f"bison version to low: {res}", RuntimeWarning)
                    else:
                        self.bin_path = self.MAC_GCC_PATH
                else:
                    self.bin_path = self.MAC_GCC_PATH
            else:
                raise RuntimeError("bison don't exist")
        elif sys.platform.startswith("linux"):
            pass

    def build(self):
        if self.bin_path is None:
            raise RuntimeError("run env_checker first")
        py_include = sysconfig.get_python_inc()
        plat_py_include = sysconfig.get_python_inc(plat_specific=1)
        self.include_dirs.extend(py_include.split(os.path.pathsep))
        if plat_py_include != py_include:
            self.include_dirs.extend(
                plat_py_include.split(os.path.pathsep))

        output = os.path.join(self.temp_dir, f"{self.name}.so")
        cmds = [
            self.bin_path,
            '-fPIC',
            '-shared',
            self.flex.output_c,
            self.bison.output_c,
            *[f"-I{i}" for i in self.include_dirs],
            '-o',
            output
        ]
        proc = self.run_cmd(cmds, env=self.flex.run_env)
        out, err = proc.communicate()
        print(f"error code: {proc.returncode} \n"
              f" {out.decode(sys.getdefaultencoding())}"
              f" {err.decode(sys.getdefaultencoding())}")
