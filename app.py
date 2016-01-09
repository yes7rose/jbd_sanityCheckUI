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
import os, sys
basePath = os.path.realpath(__file__)
basePath = basePath.split(os.path.sep)
basePath = "\\".join(basePath[:-1])

sys.path.append(basePath)

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

    def run_app(self):
        """
        Callback from when the menu is clicked.
        """
        import sanityChecker as sanity
        self.myWin = sanity.SanityUI()
        self.myWin.show()
