import unittest
import subprocess

class AppTest(unittest.TestCase):

    def testInit(self):
        self.assertEqual(1, 1)
        subprocess.check_call([
            "python",
            "-c",
            "__import__('compiler').parse(open('../jungle.py').read())"
          ]
        )
if __name__ == '__main__':
    unittest.main()
