# -*- encoding:utf8 -*-

from requests import get, post
from requests.exceptions import Timeout
from json import loads, dumps
import logging
import time

TIMEOUT_RETRY_SECONDS = 5
MAX_TIMEOUT_RETRIES = 3
logging.basicConfig(level=logging.INFO)
handler = logging.FileHandler('/tmp/apiname.log')
logger = logging.getLogger(__name__)
logger.addHandler(handler)

# Methods allowed
GET = 'get'
POST = 'post'
METHODS = {GET: get, POST: post}

# Base API url
API_URL = 'https://api.name.com/api'
# Default API user
API_USER = None
# Default API token
API_TOKEN = None

class DNSRecord(object):
    """
        DNS Record model. Describes default values of a record
        in dns infraestructure, and provides a valid json describing
        the record
    """

    def __init__(self, domain=None, hostname=None, rtype='CNAME', content=None,
            ttl=300, priority=None, record_id=None, create_date=None):
        """
            Instance a DNS Record with its default values
             * record_id (string) = unique record id
             * domain (string) = Record domain (Null)
             * hostname (string) = Subdomain (Null)
             * rtype (string) = Type of record (CNAME)
             * content (string) = Record content: elb name, IP, etc (Null)
             * ttl (int) = Default TTL (300)
             * priority (int) = Default priority (Null)
             * create_date (date) = Record created date
        """
        self.record_id = record_id
        self.domain = domain
        self.hostname = hostname
        self.rtype = rtype
        self.content = content
        self.ttl = ttl
        self.priority = priority
        self.create_date = create_date

    def __str__(self):
        """
            DNSRecord unicode representation
        """
        return u"%s.%s (%s)" % (self.hostname, self.domain, self.rtype)

    def post_data(self):
        """
            Return a valid dict for creating dns record in name API
            {
             'hostname': <subdomain>,
             'type': <record type>,
             'content': <record content>,
             'ttl': <TTL>,
             'priority': <priority>
            }
        """
        return {'hostname': self.hostname, 'priority': self.priority,
            'content': self.content, 'ttl': self.ttl, 'type': self.rtype}

    @staticmethod
    def create_from_raw(raw_dict):
        """
            Creates a new DNSRecord instance given a raw dict with field values.
            Key value map is:
             domain (string): record domain
             record_id (int): unique ID
             name (string): subdomain.domain.com
             type (string): DNS record type (CNAME, A, MX, etc)
             content (string): DNS record content
             ttl (string): DNS record TTL
             priority (string): DNS record priority
             updated_date (string): last update record date
            * Args
             - raw_dict (dict): dict with key value map
            * Outuput
        """
        raw_dict['rtype'] = raw_dict.pop('type') # Remap type to rtype
        raw_dict['hostname'] = raw_dict.pop('name') # Remap name to hostname
        return DNSRecord(**raw_dict)

class APIName(object):
    """
        Manage Name.com API connection.
        Features:
         - List dns records
         - Add dns records
         - Delete dns records
         - Update dns records
        Public methods:
         * list_dns_records
         * delete_dns_record
         * update_dns_record
         * create_dns_record
        Private methods:
         * _do_request
    """

    conn = None

    def __init__(self, url=API_URL, username=API_USER, token=API_TOKEN):
        """
            Initializes base url and creates authentication headers
        """
        self.base_url = url
        self.headers = {'Api-Username': username, 'Api-Token': token}

    def __str__(self):
        """
            APIName unicode representation
        """
        return u"%s (%s)" % (self.base_url, self.headers['Api-Username'])

    def _postprocess(self, response, method_name):
        """
            Post-process a request response, so log error
            if they happend and return valid data
            * Args:
             - response (requests.Response): http response
             - method_name (string): ancestor method (for logging)
            * Output:
             - data (dict): response data
             - None: error in response
        """
        if response:
            _result = loads(response.content)
            _respdict = _result.pop('result')
            if _respdict['code'] == 100:
                if not _result:
                    return True
                return _result
            _msg = u"Error in %s method: %s" % (method_name, _respdict['message'])
            logger.error(_msg)
        return False

    def _do_request(self, url, method=GET, payload=None):
        """
            Wrapper for requests get/post methods.
            This method takes care of requests errors.
            * Args:
             - url (string): API url to check (full url)
             - method (const string): GET or POST method
             - data (dict): payload for post request
            * Output:
             - result (Response): response of request
        """
        params = {'headers': self.headers}
        if payload:
            params['data'] = dumps(payload)

        _attemp = 0
        while _attemp < MAX_TIMEOUT_RETRIES:
            try:
                response = METHODS[method](url, **params)
                break
            except Timeout:
                logging.warn(u"Timeout error getting %s, retry...", url)
                _attemp += 1
                time.sleep(TIMEOUT_RETRY_SECONDS)
        if _attemp >= MAX_TIMEOUT_RETRIES:
            logger.error(u"Max retries getting %s", url)
            return None

        if response and response.status_code == 200:
            return response
        try:
            _msg = u"Error %s in request %s %s: %s" % (response.status_code,
                method.upper(), url, response.content)
        except UnicodeDecodeError:
            _msg = u"Error %s in request %s %s: %s" % (response.status_code,
                method.upper(), url, response.reason)
        logger.error(_msg)
        return None

    def get_dns_record(self, domain, record_id):
        """
            Retrieve dns record from a record_id given
            * Args:
             - record_id (string): valid name dns record id
            * Output:
             - None: No record was found or error
             - record (DNSRecord): dns record matched
        """
        records = self.list_dns_records(domain)
        for record in records:
            if record.record_id == record_id:
                return record
        return None

    def find_dns_record(self, domain, content):
        """
            Find a dns record from a domain given which matchs with content
            * Args:
             - domain (string): valid domain from name.com
             - content (string): record content to find
            * Output:
             - None: No record was found or error
             - record (DNSRecord): dns record matched
        """
        records = self.list_dns_records(domain)
        for record in records:
            if content == record.content:
                return record
        return None

    def list_dns_records(self, domain):
        """
            Find all dns records from a domain given or
            try to find a record which matchs with content
            * Args:
             - domain (string): valid domain from name.com
            * Output:
             - records (Array): list of domain dns records
        """
        _result = self._do_request(self.base_url + "/dns/list/%s" % domain)
        _data = self._postprocess(_result, 'list_dns_records')
        _records = []
        if _data:
            for row in _data[u'records']:
                row['domain'] = domain
                _rec = DNSRecord.create_from_raw(row)
                _records.append(_rec)
        return _records

    def delete_dns_record(self, domain, record_id):
        """
            Delete a domain dns record given a record_id
            * Args:
             - domain (string): valid domain from name.com
             - record_id (string): valid record_id of dns record
            * Output:
             - True (bool): record was deleted
             - False (bool): there was an error in process
        """
        _result = self._do_request(self.base_url + "/dns/delete/%s" % domain,
            POST, {'record_id': record_id})
        _data = self._postprocess(_result, 'delete_dns_record')
        if _data:
            return True
        return False

    def create_dns_record(self, domain, record):
        """
            Create a new dns record given a DNSRecord instance.
            * Args:
             - domain (string): valid domain from name.com
             - record (DNSRecord): values of record items
            * Output:
             - DNSRecord (bool): record was properly created
             - False (bool): record was not created (error thown)
        """
        _result = self._do_request(self.base_url + "/dns/create/%s" % domain,
            POST, record.post_data())
        _data = self._postprocess(_result, 'create_dns_record')
        if _data:
            _data['domain'] = domain
            return DNSRecord.create_from_raw(_data)
        return False

    def update_dns_record(self, domain, content, record):
        """
            Update a dns record for a domain given. First current record
            is deleted; later on a new one is created using create_dns_record
            * Args:
             - domain (string): valid domain from name.com
             - content (string): content of record to update
             - record (DNSRecord): values of record items
            * Output:
             - True (bool): record was properly updated
             - False (bool): record was not updated (error thrown)
        """
        _found = self.find_dns_record(domain, content)
        if _found:
            self.delete_dns_record(domain, _found.record_id)
        return self.create_dns_record(domain, record)

    def update_nameservers(self, domain, nameservers):
        """
            Update nameservers, setting param list as default
            nameservers
            * Args:
             - domain (string): valid domain from name.com
             - nameservers (list): list of default nameserver
            * Output
             - True (bool): default nameservers updated
             - False (bool): there was an error in process
        """
        _url = self.base_url + '/domain/update_nameservers/' + domain
        _result = self._do_request(_url, POST, {'nameservers': nameservers})
        _data = self._postprocess(_result, 'update_nameservers')
        if _data:
            return True
        return False

    def get_domain(self, domain, check=True):
        """
            Retrieve domain info (creation and expire dates, locked,
            nameservers, etc). Check if a domain exists by default
            * Args:
             - domain (string): valid domain from name.com
             - check (bool): retrieve info or just check if exists (true)
            * Output:
             - False (bool): domain was not found
             - True (bool): domain was found (check = True)
             - Response (request.Response): domain was found (check = False)
        """
        _response = self._do_request(self.base_url + "/domain/get/%s" % domain)
        _data = self._postprocess(_response, 'get_domain')
        if not _data:
            return False
        if check:
            return True
        return _data
