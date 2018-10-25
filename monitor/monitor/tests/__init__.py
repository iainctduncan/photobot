import ConfigParser
import unittest
import webtest
import pkg_resources

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import configure_mappers

import logging
log = logging.getLogger()

TEST_INI = 'test.ini'

class FunctionalTestSuite(unittest.TestCase):
    """
    base class for functional test suite with db seeding"
    """

    # derived class needs to set this to the package of the app under test
    # IE app_module = examp.app
    app_package = None
    # derived class can put extra settings in here
    override_settings = {}

    def __init__(self, *args, **kwargs):
        super(FunctionalTestSuite, self).__init__(*args, **kwargs)
        self._settings = None

    @classmethod
    def _read_test_settings(cls):
        try:
            test_settings_fileobj = pkg_resources.resource_stream(cls.app_package.__name__, '/../../' + TEST_INI)
        except AttributeError as e:
            raise Exception("app_package not defined in %s" % cls.__name__)
        config = ConfigParser.ConfigParser()
        config.readfp(test_settings_fileobj)
        return dict(config.items('app:main'))

    @classmethod
    def setUpClass(cls):
        "class level setUp creates tables"
        cls.settings = cls._read_test_settings()
        cls.settings.update(cls.override_settings)
        map_domain_model()
        cls.engine = SQLAEngine(
            db_url=cls.settings.get('sqlalchemy.url'),
            autocommit=False,
            autoflush=False
        )._engine
        cls.session_factory = sessionmaker(bind=cls.engine)

    @classmethod
    def tearDownClass(cls):
        "dispose of engine"
        cls.engine.dispose()

    @classmethod
    def init_db(cls):
        "initialize the database and create sessions, normally called from setUp"
        # drop and recreate tables once per test
        # NB: this has to be done differently for postgres because it's a constraint nazi
        metadata.drop_all(bind=cls.engine)
        metadata.create_all(bind=cls.engine)

    def init_dbsessions(self):
        "init seed and confirm sessions, normally called from setUp"
        # create sessions for seeding and separate for confirming
        self.seed_dbs = self.session_factory()
        self.confirm_dbs = self.session_factory()

    def init_app(self):
        "init test wsgi app, normally called from setUp"
        self.app = self.app_package.main({}, **self.settings)
        self.registry = self.get_registry(self.app)
        self.testapp = webtest.TestApp(self.app)

    def setUp(self):
        "run setup prior to each test"
        # for tests where we want fresh db on *every* test, we use this
        self.init_db()
        self.init_dbsessions()
        self.init_app()

    def tearDown(self):
        "clean up after each test"
        self.seed_dbs.close()
        self.confirm_dbs.close()

    def get_registry(self, app):
        # find the registry within a stack of wrapped apps
        source = app
        while hasattr(source, 'app') or hasattr(source, 'application'):
            try:
                source = getattr(source, 'app')
            except:
                source = getattr(source, 'application')
        return source.registry
