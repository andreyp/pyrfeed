import unittest
from pyrfeed.config import Config

class TestConfig(unittest.TestCase) :
    def setUp(self) :
        self._config = Config()
        self._test_key = 'KEY_THAT_SHOULD_NOT_EXIST'
        del self._config[self._test_key]

    def testNotExist(self) :
        self.assertEqual(self._config[self._test_key],None)

    def testWriteRead(self) :
        self.assertEqual(self._config[self._test_key],None,"Verification de l'etat stable")
        for value in ('murf','chonk','plank','goink') :
            self._config[self._test_key] = value
            self.assertEqual(self._config[self._test_key],value)
        del self._config[self._test_key]
        self.assertEqual(self._config[self._test_key],None,"Retour dans l'etat stable")

    def testWriteReadLoadSave(self) :
        self._config.save()
        self.assertEqual(self._config[self._test_key],None,"Verification de l'etat stable")

        configTest = Config()

        for value in ('murf','chonk','plank','goink') :
            self._config[self._test_key] = value
            self._config.save()
            configTest.load()
            self.assertNotEqual(configTest[self._test_key],'raf')
            self.assertEqual(configTest[self._test_key],value)

        configTest = None

        del self._config[self._test_key]
        self._config.save()
        self.assertEqual(self._config[self._test_key],None,"Retour dans l'etat stable")

    def testPersistance(self) :
        self._config.save()
        self.assertEqual(self._config[self._test_key],None,"Verification de l'etat stable")

        configTest = Config(['--'+self._test_key])
        configTest.save()

        self.assertEqual(configTest[self._test_key],True)
        self.assertNotEqual(self._config[self._test_key],True)

        self._config[self._test_key] = 'pluk'
        self._config.save()
        configTest.load()

        self.assertEqual(configTest[self._test_key],True)
        self.assertEqual(self._config[self._test_key],'pluk')

        configTest[self._test_key] = 'manf'
        configTest.save()
        self._config.load()

        self.assertEqual(configTest[self._test_key],'manf')
        self.assertEqual(self._config[self._test_key],'manf')

        configTest = None

        del self._config[self._test_key]
        self._config.save()
        self.assertEqual(self._config[self._test_key],None,"Retour dans l'etat stable")

    def testPersistanceArg(self) :
        self._config.save()
        self.assertEqual(self._config[self._test_key],None,"Verification de l'etat stable")

        configTest = Config(['--'+self._test_key+'=Praf=Test'])
        configTest.save()

        self.assertEqual(configTest[self._test_key],'Praf=Test')
        self.assertNotEqual(self._config[self._test_key],'Praf=Test')

        self._config[self._test_key] = 'pluk'
        self._config.save()
        configTest.load()

        self.assertEqual(configTest[self._test_key],'Praf=Test')
        self.assertEqual(self._config[self._test_key],'pluk')

        configTest[self._test_key] = 'manf'
        configTest.save()
        self._config.load()

        self.assertEqual(configTest[self._test_key],'manf')
        self.assertEqual(self._config[self._test_key],'manf')

        configTest = None

        del self._config[self._test_key]
        self._config.save()
        self.assertEqual(self._config[self._test_key],None,"Retour dans l'etat stable")

if __name__ == '__main__':
    unittest.main()

