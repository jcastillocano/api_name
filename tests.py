# -*- encoding: utf-8 -*-

import unittest
from api_name.api import APIName, DNSRecord

class APINameTest(unittest.TestCase):
    """
        Tests for APIName class main functionalities
    """
    def setUp(self):
        self.domain = 'test.com'
        self.record = DNSRecord(domain=self.domain, hostname='www.test.com', \
            content='test2.com', record_id='1')

    ##############################################################
    # DNSRecord tests
    ##############################################################
    def test_post_data(self):
        "Test post_data DNSRecord method"
        _result = {'hostname': 'www.test.com', 'priority': None,
            'content': 'test2.com', 'ttl': 300, 'type': 'CNAME'}
        self.assertEqual(_result, self.record.post_data())

    def test_create_from_raw(self):
        "Test create_from_raw DNSRecord method"
        _raw_dict = {'record_id': '1', 'name': 'www.test.com', 'type': 'CNAME',
            'content': 'test2.com', 'ttl': 300, 'priority': None,
            'domain': 'test.com'}
        _record = DNSRecord.create_from_raw(_raw_dict)
        for _fd in ['domain', 'hostname', 'content', 'record_id']:
            self.assertEqual(getattr(self.record, _fd), getattr(_record, _fd))

    ##############################################################
    # APIName tests
    ##############################################################

    #TODO: tests

if __name__ == '__main__':
    unittest.main()
