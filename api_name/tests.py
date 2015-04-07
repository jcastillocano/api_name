# -*- encoding:utf8 -*-

from api import DNSRecord, APIName
import unittest
import mock

class MockResponse(object):
    """
        Mock requests.response object
    """
    def __init__(self):
        self.status_code = 200
        self.content = '{"records":[{"id":1,"content":"www.test.com"}]}'

class TestAPIName(unittest.TestCase):
    """
        DNSRecord and APIName tests
    """

    def setUp(self):
        """
            Initial domain and record setup
        """
        self.domain = 'mydomain.com'
        self.record = DNSRecord(domain=self.domain, hostname='www', rtype='A',
            content='192.168.0.10')
        self.api = APIName(username='foo', token='bar')

    ####################################################################
    # DNSRecord
    ####################################################################
    def test_record_defaults(self):
        """
            Check default values for a new record
        """
        value_list = (
            ('domain', self.domain), ('hostname', 'www'), ('rtype', 'A'),
            ('content', '192.168.0.10'), ('ttl', 300), ('priority', None),
        )
        for param, value in value_list:
            _msg = u"Param %s: default content doesnt match" % param
            self.assertEqual(getattr(self.record, param), value, _msg)

    def test_post_data(self):
        """
            Test DNSRecord post_data method
        """
        _msg = u'DNSRecord post_data doesnt match with requirements'
        _result = {'hostname': 'www', 'type': 'A', 'content': '192.168.0.10',
            'ttl': 300, 'priority': None}
        self.assertEqual(self.record.post_data(), _result, _msg)

    def test_create_from_raw(self):
        "Test create_from_raw DNSRecord method"
        _raw_dict = {'record_id': '1', 'name': 'www.test.com', 'type': 'CNAME',
            'content': 'test2.com', 'ttl': 300, 'priority': None,
            'domain': 'test.com'}
        _record = DNSRecord.create_from_raw(_raw_dict)
        for _fd in ['domain', 'hostname', 'content', 'record_id']:
            self.assertEqual(getattr(self.record, _fd), getattr(_record, _fd))

    ####################################################################
    # APIName
    ####################################################################
    def test_headers(self):
        """
            Test header username and token
        """
        for key, value in (('Api-Username', 'foo'), ('Api-Token', 'bar')):
            _msg = u"%s doesnt not match or not exist" % key
            self.assertEqual(self.api.headers[key], value, _msg)

    #FIXME: make dns record management tests with mock

####################################################################
# Main method
####################################################################
if __name__ == '__main__':
    unittest.main()
