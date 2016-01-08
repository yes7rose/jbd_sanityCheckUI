'''
Created 2016
@author: jamesd
'''
from getpass import getuser
import os
USERNAME = getuser()
CONSTRAINTS = ('parentConstraint', 'pointConstraint', 'orientConstraint',
               'scaleConstraint', 'pointOnPolyConstraint', 'geometryConstraint',
               'normalConstraint', 'tangentConstraint', 'poleVectorConstraint',
               'aimConstraint')
GROUP_SUFFIX = 'hrc'
GEOMETRY_SUFFIX = 'geo'
RIG_CTRL_SUFFIX = 'ctrl'
BLENDSHAPE_SUFFIX = 'BLN'
NURBSCRV_SUFFIX = 'crv'
IMPORT_SUFFIX = 'importDELME'
SHOTCAM_SUFFIX = 'shotCam'
L_PREFIX = 'L'
R_PREFIX = 'R'
SRT_SUFFIX = 'srt'
SRTBUFFER_SUFFIX = 'srtBuffer'

basePath = os.path.realpath(__file__)
basePath = basePath.split(os.path.sep)
basePath = "\\".join(basePath[:-2])
ICONPATH = "%s\\icons\\" % basePath
