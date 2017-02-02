import unittest
import subprocess

class AppTest(unittest.TestCase):

    def testInit(self):
        self.assertEqual(1, 1)
        subprocess.check_output(
            "/usr/bin/env python -m py_compile ../jungle.py",
            stderr=subprocess.STDOUT,
            shell=True)

if __name__ == '__main__':
    unittest.main()
