#! /usr/bin/python
# -*- encoding:utf8 -*-

from requests import get, post
from json import loads, dumps
import logging

logger = logging.getLogger(__name__)

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

class DNSRecord:
    """
        DNS Record model. Describes default values of a record
        in dns infraestructure, and provides a valid json describing
        the record
    """

    def __init__(self, domain=None, hostname=None, rtype='CNAME',
        content=None, ttl=300, priority=None):
        """
            Instance a DNS Record with its default values
             * domain (string) = Record domain (Null)
             * hostname (string) = Subdomain (Null)
             * rtype (string) = Type of record (CNAME)
             * content (string) = Record content: elb name, IP, etc (Null)
             * ttl (int) = Default TTL (300)
             * priority (int) = Default priority (Null)
        """
        self.domain = domain
        self.hostname = hostname
        self.rtype = rtype
        self.content = content
        self.ttl = ttl
        self.priority = priority

    def __unicode(self):
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


class APIName:
    """
        Manage Name.com API connection.
        Features:
         - List dns records
         - Add dns records
         - Delete dns records
         - Update dns records
        Public methods:
         * find_dns_records
         * delete_dns_record
         * update_dns_record
         * create_dns_record
         * do_request
    """

    conn = None

    def __init__(self, url=API_URL, username=API_USER, token=API_TOKEN):
        """
            Initializes base url and creates authentication headers
        """
        self.base_url = url
        self.headers = {'Api-Username': username, 'Api-Token': token}

    def __unicode__(self):
        """
            APIName unicode representation
        """
        return u"%s (%s)" % (self.base_url, self.headers['Api-Username'])

    def do_request(self, url, method=GET, payload=None):
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
        response = METHODS[method](url, **params)
        if response and response.status_code == 200:
            return response
        _msg = u"Error %s in request %s %s: %s" % (response.status_code,
            method.upper(), url, response.content)
        logger.error(_msg)
        return None

    def find_dns_records(self, domain, find_content=False):
        """
            Find all dns records from a domain given or
            try to find a record which matchs with content
            * Args:
             - domain (string): valid domain from name.com
             - find_content (string) [Optional]: record content to find
            * Output:
             - None: if find_content was given and no record was found or error
             - records (Array): list of domain dns records
        """
        _result = self.do_request(self.base_url + "/dns/list/%s" % domain)
        if _result:
            records = []
            _data = loads(_result.content)
            for row in _data[u'records']:
                _rec = {'id': row[u'record_id'], 'content': row[u'content']}
                if find_content and _rec['content'] == find_content:
                    return row
                records.append(_rec)
            # If find_content was supplied and we arrive here means that
            # no record was found
            if find_content:
                return None
            # Return dns record list
            return records
        return None

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
        _result = self.do_request(self.base_url + "/dns/delete/%s" % domain,
            POST, {'record_id': record_id})
        if _result:
            response = loads(_result.content)
            if response['result']['code'] == 100:
                return True
            _msg = response['result']['message']
            logger.error(_msg)
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
        _found = self.find_dns_records(domain, record)
        if _found:
            self.delete_dns_record(domain, _found[u'record_id'])
        return self.create_dns_record(domain, record)

    def create_dns_record(self, domain, record):
        """
            Create a new dns record given a DNSRecord instance.
            * Args:
             - domain (string): valid domain from name.com
             - record (DNSRecord): values of record items
            * Output:
             - True (bool): record was properly created
             - False (bool): record was not created (error thown)
        """
        return self.do_request(self.base_url + "/dns/create/%s" % domain,
            POST, record.post_data())

