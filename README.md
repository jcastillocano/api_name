API Name.com
=======================

Python API for name.com API v2 beta http://www.name.com/reseller

Installation
-----------------------

You can install this package either pip or downloading it:

 * pip install git+https://github.com/jccastillocano/api_name.git
 * ```wget https://github.com/jccastillocano/api_name/archive/master.zip &&
   gzip -d master.zip && unzip master.zip && cd api_name-master && python setup.py install```

Configuration
-----------------------

You dont need any config file; only supply *username* and *api_token* when
instance an API class in init method. Also you can use API dev version
if you supply api dev url.

> api = APIName(username='foo', api_token='1234bar')

Notes
-----------------------

This API is for test use, DO NO GUARANTEE full management of name.com API.
You need first to request an account in https://www.name.com/account/create
and then you can apply for API access in http://www.name.com/reseller/apply.
A manual, username and api_token will be sent to your email address with
all needs.

This API is not complete. Only DNS methods (due to business requeriments)
are implemented, and some domain methods. Full API implementation will be
done in the next months.
