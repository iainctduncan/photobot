import unittest
import requests
import webtest
from monitor.tests import FunctionalTestSuite
import json

import pdb

class TestPing(unittest.TestCase):

    host = "http://127.0.0.1:6543"

    def xtest_pass(self):
        assert True

    def xtest_dashboard(self):
        url = self.host + "/"
        res = requests.get(url)

    def test_ping(self):
        uid = "24f2447e-20b2-4a6b-a1b7-7a336abdb498"
        data = {
            'installation_uid': uid,
            'status': 'OK'
        }
        url = self.host + "/ping"
        res = requests.post(url, data=data)
        assert res.status == 200
        pdb.set_trace()
