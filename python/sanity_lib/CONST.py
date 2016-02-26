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

GROUP_SUFFIX = {
                "master": 'hrc',
                "secondary": ['grp', 'srt', 'srtBuffer', 'input', 'output', 'def']
                }
GEOMETRY_SUFFIX = {
                "master": 'geo',
                "secondary": ['bln', 'Base']
                }
RIG_CTRL_SUFFIX = {
                "master": 'ctrl',
                "secondary": 'ctl'
                }
BLENDSHAPE_SUFFIX = {
                "master": 'BLN',
                "secondary": ['bln']
                }
NURBSCRV_SUFFIX = {
                "master": 'crv',
                "secondary": ['curve', 'ctrl', 'jnt']
                }
IMPORT_SUFFIX = {
                "master": 'importDELME',
                "secondary": ['imp']
                }
SHOTCAM_SUFFIX = {
                "master": 'shotCam',
                "secondary": ['shcam']
                }
SHOTCAM_SUFFIX = {
                "master": 'srt',
                "secondary": ['SRT']
                }
SRTBUFFER_SUFFIX = {
                "master": 'srtBuffer',
                "secondary": ['srtBuffer']
                }
JOINT_SUFFIX = {
                "master": 'jnt',
                "secondary": ['JNT']
                }
L_PREFIX = 'L'
R_PREFIX = 'R'
EXTRAS = ['visibility']
VIS = ['visibility']

basePath = os.path.realpath(__file__)
basePath = basePath.split(os.path.sep)
basePath = "\\".join(basePath[:-3])
ICONPATH = "%s\\icons\\" % basePath
