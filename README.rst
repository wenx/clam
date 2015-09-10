=======================================================
CLAM: Computational Linguistics Application Mediator
=======================================================

.. image:: https://travis-ci.org/proycon/clam.svg?branch=master
    :target: https://travis-ci.org/proycon/clam

*by Maarten van Gompel, Centre for Language and Speech Technology, Radboud University Nijmegen*

*Licensed under GPLv3*
		
**Website:** http://proycon.github.io/clam 
**Source repository:** https://github.com/proycon/clam/

CLAM allows you to quickly and transparently transform your Natural Language
Processing application into a RESTful webservice, with which both human
end-users as well as automated clients can interact. CLAM takes a description
of your system and wraps itself around the system, allowing end-users or
automated clients to upload input files to your application, start your
application with specific parameters of their choice, and download and view the
output of the application once it is completed.

CLAM is set up in a universal fashion, requiring minimal effort on the part of
the service developer. Your actual NLP application is treated as a black box,
of which only the parameters, input formats and output formats need to be
described. Your application itself needs not be network aware in any way, nor
aware of CLAM, and the handling and validation of input can be taken care of by
CLAM.

CLAM is entirely written in Python, runs on UNIX-derived systems, and is
available as open source under the GNU Public License (v3). It is set up in a
modular fashion, and offers an API, and as such is easily extendable. CLAM
communicates in a transparent XML format, and using XSL transformation offers a
full web 2.0 web-interface for human end users. 

Installation instruction can be found below. For full documentation see the
manual in ``docs/clam_manual.pdf`` , also accessible through the CLAM website
at http://proycon.github.io/clam . It is recommended to read this prior to
starting with CLAM. 


Installation
----------------

IMPORTANT NOTICE: It's discouraged to download the zip packages or tarballs
from github, install CLAM from the `Python
Package Index <http://pypi.python.org/pypi/CLAM>`_ or use git properly.

Installation On Linux 
~~~~~~~~~~~~~~~~~~~~~~~~

Easy install is part of the Python setup tools and can install CLAM globally on
your system for you from the Python Package Index. This is the easiest method
of installing CLAM, as it will automatically fetch and install any
dependencies. We recommend to use a virtual environment (``virtualenv``) if you
want to install CLAM locally as a user, if you want to install globally,
prepend the following commands with ``sudo``:

CLAM can be installed from the Python Package Index using pip. Pip is usually
part of the ``python3-pip`` package or similar. It downloads CLAM
automatically.

 $ pip3 install clam

If you already downloaded CLAM manually (from github), you can do::

 $ python3 setup.py install

If pip3 is not yet installed on your system, install it using: 
 on debian-based linux systems (including Ubuntu)::

  $ apt-get install python3-pip 
  
on RPM-based linux systems::

  $ yum install python3-pip

Note that sudo/root access is needed to install globally. Ask your system administrator
to install it. Alternatively, you can install it locally in a Python virtual
environment:

 $ virtualenv --python=python3 clamenv

 $ . clamenv/bin/activate

 (clamenv)$ pip3 install clam

 It is also possible to use Python 2.7 instead of Python 3, adapt the commands
 as necessary.
 

Installation on Mac OS X
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install a Python distribution such as `Anaconda <http://continuum.io/>`_ and follow the Linux instructions above.


Installation on Windows
~~~~~~~~~~~~~~~~~~~~~~~~~~

 Not supported, delete Windows and install a decent OS ;)
 

Running a test webservice
~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you installed CLAM using the above method, then you can launch a clam test
webservice using the development server as follows:

$ clamservice -H localhost -p 8080 clam.config.textstats
 
Navigate your browser to http://localhost:8080 and verify everything works

If any problems occur during installation regarding pycurl, then install the
pycurl package supplied by your distribution (python-pycurl on Debian/ubuntu)

Note: It is important to regularly keep CLAM up to date as fixes and
improvements are implemented on a regular basis. Update CLAM using::

or if you used pip::

 $ pip install -U clam

or if you used easy_install::

 $ easy_install -U clam


Installing a particular clam webservice for production use
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When installating a particular CLAM webservice on a new server, it is first
necessary to edit the service configuration file of the webservice and make
sure all the paths in there are set correctly for the new server. Of interest
is in particular the ROOT path, which is where user data will be stored, this
directory must exist and be writable by the webserver.

For testing, the built-in development server can be used. Suppose the
webservice configuration is in /path/to/mywebservice/ and is called
mywebservice.py, then the development server can be started as follows::

 $ clamservice -P /path/to/mywebservice mywebservice

For production, however, it is strongly recommended to embed CLAM in Apache or
nginx. This is the typically task of a system administrator, as certain skills are
necessary and assumed. All this is explained in detail in the CLAM
Manual, obtainable from http://proycon.github.io/clam/ . 




