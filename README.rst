API Name.com
=======================

Python API for name.com API v2 beta http://www.name.com/reseller

Installation
-----------------------

You can install this package either pip or setup.py:

 * pip install git+https://github.com/jccastillocano/api_name.git
 * python setup.py install

Configuration
-----------------------

You dont need any config file; only supply <username> and <api_token> when
instance an API class in init method. Also you can use API dev version
if you supply api dev url.

Notes
-----------------------

This API is not complete. Only DNS methods (due to business requeriments)
are implemented, and some domain methods. Full API implementation will be
done in the next months.
