import unittest
from deadlock import bankers_safety, request_resources, detect_deadlock

A=[[0,1,0],[2,0,0],[3,0,2],[2,1,1],[0,0,2]]
M=[[7,5,3],[3,2,2],[9,0,2],[2,2,2],[4,3,3]]
V=[3,3,2]

class Tests(unittest.TestCase):
    def test_bankers_sample_safe(self):
        r=bankers_safety(A,M,V); self.assertTrue(r["safe"]); self.assertEqual(len(r["sequence"]),5)
    def test_request_within_need(self):
        r=request_resources(A,M,V,1,[1,0,2]); self.assertTrue(r["granted"])
    def test_request_over_need_rejected(self):
        r=request_resources(A,M,V,1,[2,0,0]); self.assertFalse(r["granted"])
    def test_no_requests_no_deadlock(self):
        r=detect_deadlock(A,[[0,0,0] for _ in A],V); self.assertFalse(r["deadlock"])
    def test_unsafe_state(self):
        r=bankers_safety([[1,0]],[[1,1]],[0,0]); self.assertFalse(r["safe"])

if __name__=="__main__": unittest.main()
