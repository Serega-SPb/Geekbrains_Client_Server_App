from setuptools import setup, find_packages

setup(name="Geekbrains_CSA_server_Abissov",
      version="0.3",
      description="Geekbrains_CSA_server",
      author="Serega Abissov",
      author_email="abissovs@gmail.com",
      package_dir={'root': '.', 'server': './server',
                   'jim': './server/jim', 'ui': './server/ui', 'logs': './server/logs'},
      packages=['server', 'jim', 'ui', 'logs'],
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'yaml']
      )
