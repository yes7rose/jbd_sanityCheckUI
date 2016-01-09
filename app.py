"""
Copyright (c) 2013 James Dunlop
----------------------------------------------------
Creates a maya shotCam based off he shot name of the current context
"""
import logging
logger = logging.getLogger(__name__)
###################################
## Shotgun Imports               ##
from tank.platform import Application
import tank.templatekey
import sgtk


class SanityCheckerUI(Application):
    def init_app(self):
        # make sure that the context has an entity associated - otherwise it wont work!
        if self.context.entity is None:
            raise tank.TankError("Cannot load the SanityCheckerUI application! "
                                 "Your current context does not have an entity (e.g. "
                                 "a current Shot, current Asset etc). This app requires "
                                 "an entity as part of the context in order to work.")
        getDisplayName = self.get_setting('display_name')
        self.engine.register_command(getDisplayName, self.run_app)
        self.lib = self.import_module("sanity_lib")
        logger.info('%s Loaded...' % getDisplayName)

    def run_app(self):
        """
        Callback from when the menu is clicked.
        """
        self.lib = self.import_module("sanity_lib")
        logger.info('self.lib: %s' % self.lib)
        inprogressBar = self.lib.ProgressBarUI(title = 'Building Shotcam:')
