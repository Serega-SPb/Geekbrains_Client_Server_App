from setuptools import setup, find_packages

setup(name="Geekbrains_CSA_client_Abissov",
      version="0.3",
      description="Geekbrains_CSA_client",
      author="Serega Abissov",
      author_email="abissovs@gmail.com",
      package_dir={'root': '.', 'client': './client',
                   'jim': './client/jim', 'ui': './client/ui', 'logs': './client/logs'},
      packages=['client', 'jim', 'ui', 'logs'],
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'yaml']
      )
