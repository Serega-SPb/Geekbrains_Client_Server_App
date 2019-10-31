import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ['jim', 'ui', 'logs'],
    'namespace_packages': ['sqlalchemy.sql.default_comparator']
}
setup(
    name="Geekbrains_CSA_server",
    version="0.1",
    description="Geekbrains_CSA_server",
    options={
        "build_exe": build_exe_options
    },
    executables=[Executable('start_server.py',
                            base='Win32GUI',
                            targetName='server.exe',
                            )]
)
