.. image:: logo/crono_logo.png

Cronohub
========

Archive from anywhere to anywhere using the power of plugins.

How does it work?
=================

Cronohub in it's own is useless. It's power comes from plugins located here
plugins_repository_. These plugins are used as **source** and **target**.
Examples are under the plugins_ sections. Once an appropriate plugin is
selected for downloading and uploading, cronohub takes care of the rest.

For example to download all repositories for a user from github and then
upload all those repositories to an s3 bucket with timestamp cronohub would
be used like this:

.. code-block:: bash

    cronohub -s github -t s3

The github plugin takes care of all of the necessary authentication and
parallel downloading of all repositories. The plugin also has the ability
to filter out repos that the user whishes to archive. It's all based on
the plugin. For more information, locate the plugin and read it's README.

Install
=======

Installation is simply calling:

.. code-block:: bash

    pip install cronohub


Usage
=====

To see a help of cronohub simply access the help screen.

.. code-block:: bash

    cronohub -h


.. _plugins:

Plugins
=======

The plugins are the soul of cronohub. They are constantly added and can be
very specific and for a single purpose or can be for a wider audience.
Cronohub only provides a platform for all these plugins to exist and work
together. Cronohub is a mediator in this case.

For more information please read the plugin's readme section that explains
how they work and how a new one can be added and where they need to be
located in order or cronohub the pick them up.

.. _plugins_repository: https://github.com/cronohub/plugins
