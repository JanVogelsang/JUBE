JUBE Benchmarking Environment
Copyright (C) 2008-2018
Forschungszentrum Juelich GmbH, Juelich Supercomputing Centre
http://www.fz-juelich.de/jsc/jube

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see http://www.gnu.org/licenses/.

----

# Prerequisites

JUBE version 2 is written in the Python programming language.

You need Python 2.7 or Python 3.2 (or a higher version) to run the program.

You also can use Python 2.6 to run JUBE. In this case you had to add the argparse-module (https://pypi.python.org/pypi/argparse) to your Python module library on your own.

# Installation

After download, unpack the distribution file `JUBE-<version>.tar.gz` with:

```bash
tar -xf JUBE-<version>.tar.gz
```

You can install the files to your `$HOME/.local` directory by using:

```bash
cd JUBE-<version>
python setup.py install --user
```


`$HOME/.local/bin` must be inside your `$PATH` environment variable to use JUBE in an easy way.

Instead you can also specify a self defined path prefix:

```bash
python setup.py install --prefix=<some_path>
```

You might be asked during the installation to add your path (and some subfolders) to the `$PYTHONPATH` environment variable (this should be stored in your profile settings):


```bash
export PYTHONPATH=<needed_path>:$PYTHONPATH
```

In addition it is useful to also set the `$PATH` variable again.

To check the installation you can run:


```
jube --version
```

Without the `--user` or `--prefix` argument, JUBE will be installed in the standard system path for Python packages.

# Further Information

For further information please see the documentation: http://www.fz-juelich.de/jsc/jube

Contact: [jube.jsc@fz-juelich.de](mailto:jube.jsc@fz-juelich.de)
