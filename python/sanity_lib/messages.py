import maya.cmds as cmds
import logging
logger = logging.getLogger(__name__)
FST=500
FOT=2000

def stdError(header, message, color = "#B00000"):
    #msg = '<center><span style=\"color: %s ;\">%s</span>\n%s</center>' % (color, header, message)
    msg = '<center><span style=\"color: %s ;\">%s</span></center><left>\n%s</left>' % (color, header, message)
    cmds.inViewMessage(amg = msg, pos = 'midCenter', fade = True, fst = FST, fot = FOT)
    logger.warning('%s %s' % (header, message))

def exceptionError(header, message, color = "#B00000"):
    msg = '<center><span style=\"color: %s ;\">%s</span></center><left>\n%s</left>' % (color, header, message)
    cmds.inViewMessage(amg = msg, pos = 'midCenter', fade = True, fst = FST, fot = FOT)
    cmds.warning('%s %s' % (header, message))
    logger.warning('%s %s' % (header, message))
    raise Exception, '%s %s' % (header, message)

def success(header = 'Success', message = '', color = "#00CC00"):
    msg = '<center><span style=\"color: %s ;\">%s</span></center><left>\n%s</left>' % (color, header, message)
    #msg = '<center><span style=\"color: %s ;\">%s</span>\n%s</center>' % (color, header, message)
    cmds.inViewMessage(amg = msg, pos = 'midCenter', fade = True, fst = FST, fot = FOT)