import os
import sys

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from torch.utils.cpp_extension import BuildExtension, CUDAExtension

import torch

setup(
    name='server_torch_c',
    ext_modules=[
        CUDAExtension(
            'server_torch_c',
            define_macros=[
                ('USE_CUDA', '1'),
                ('_GLIBCXX_USE_CXX11_ABI', str(int(torch.compiled_with_cxx11_abi())))
            ],
            include_dirs=[
                '../../..',
                '/usr/local/lib'
            ],
            sources=[
                'interface.cpp',
                '../operations.cpp',
                '../core_loop.cpp',
                '../cache_agent.cpp',
                '../lb_agent.cpp',
                '../../../utils/tcp/tcp.cpp',
                '../../../utils/shared_memory/shared_memory.cpp',
                '../../../utils/memory_manager/memory_manager.cpp'
            ],
            extra_compile_args=[

            ],
            extra_link_args=[

            ],
            extra_objects=[

            ],
            library_dirs=[

            ],
            libraries=[
                'pthread',
                'rt'
            ]
        )
    ],
    cmdclass={
        'build_ext': BuildExtension
    }
)