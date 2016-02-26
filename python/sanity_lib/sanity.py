'''
@author: jamesd
'''
import logging
logger = logging.getLogger(__name__)
import re, yaml, os
try:
    import maya.cmds as cmds
    import CONST as CONST
    reload(CONST)
except:
    logger.warning('Failed to import custom libs')
    print 'Failed to import custom maya libs. Are you running this application inside maya??'

IGNORETYPES = ['tweak', 'objectTypeFilter', 'objectSet', 'dynController', 'hyperView',
              'defaultRenderUtilityList', 'postProcessList', 'groupId',
              'sequenceManager', 'hyperGraphInfo', 'defaultTextureList', 'shaderGlow',
              'objectScriptFilter', 'defaultRenderingList', 'lambert', 'renderGlobalsList',
              'hyperLayout', 'groupParts', 'defaultShaderList', 'lightList', 'objectNameFilter',
              'lightLinker', 'dof', 'particleCloud', 'defaultLightList', 'time', 'materialInfo',
              'phong', 'blinn', 'phongE', 'objectMultiFilter', 'selectionListOperator', 'objectRenderFilter',
              'lambert', 'brush', 'renderLayerManager', 'renderLayer', 'script']

def loadNodeData():
    myPath = os.path.realpath(__file__)
    myPath = myPath.split(os.path.sep)
    myPath = "/".join(myPath[:-1])
    myFile = "{}/nodeTypes.yaml".format(myPath)
    f = open(myFile, "r")
    data = yaml.load(f)
    return data

def collectSanityData():
    data = {}

    ## DupNames
    data['duplicateNames'] = [node for node in cmds.ls(sn = 1, dag = 1)] or []

    ## Mesh Shapes
    data['mesh'] = [mesh for mesh in cmds.ls(type='mesh', l = True) if not cmds.getAttr('%s.intermediateObject' % mesh)] or []

    ## Groups
    data['transform'] = [xf for xf in cmds.ls(type='transform', l = True) if cmds.nodeType(xf) not in CONST.CONSTRAINTS and cmds.nodeType(xf) != 'joint' and cmds.nodeType(xf) != 'ikEffector'] or []

    ## DisplayLayers
    data['displaylayers'] = [dl for dl in cmds.ls(type='displayLayer', l = True)] or []

    ## Nurbs Curves
    data['nurbsCurve'] = [eachCrv for eachCrv in cmds.ls(type='nurbsCurve')] or []

    ## Constraints
    for cstType in CONST.CONSTRAINTS:
        data[cstType] = [eachCST for eachCST in cmds.ls(type = cstType, l = True)] or []

    ## Intermediate Objects
    data['intermediateObject'] = [mesh for mesh in cmds.ls(type='mesh', l = True) if cmds.getAttr('%s.intermediateObject' % mesh)] or []

    ##  / Reference / DisplayLayers / Joints / Anim Curves
    types = ['displayLayer', 'reference', 'joint', 'animCurveTA', 'animCurveTL', 'animCurveTU']
    for eachType in types:
        data[eachType] = [eachNode for eachNode in cmds.ls(type = eachType, l = True)] or []

    data['pastedNodes'] = [eachNode for eachNode in cmds.ls() if 'pasted' in eachNode]

    data["transformGeometry"] = cmds.ls(type = 'transformGeometry', l = True)

    data["endingWith##"] = [node for node in cmds.ls(l=True) if re.search(r'\d+$', node) and cmds.nodeType(node) not in IGNORETYPES] or []

    data["unknown"] = cmds.ls(type = 'unknown', l = True) or []

    data["joint"] = cmds.ls(type = 'joint', l = True) or []

    return data

def checkSuffix(data, suffixes, checkParent, returnParentName):
    """
    Check for bad grp names based on the suffixes in the CONST file.
    :param data: the sanity data collected from scene. Dict from collectSanityData
    :return:
    """
    errors = []
    for eachNode in data:
        parentNode = cmds.listRelatives(eachNode, parent = True, f = True)[0]
        if checkParent:
            if not validSuffix(suffixes, parentNode):
                if returnParentName:
                    if parentNode not in errors:
                        errors.extend([parentNode])
                else:
                    errors.extend([eachNode])

        else:
            if not validSuffix(suffixes, eachNode):
                if returnParentName:
                    if parentNode not in errors:
                        errors.extend([parentNode])
                else:
                    errors.extend([eachNode])
    return errors

def checkGrpSuffix(data):
    """
    Check for bad grp names based on the suffixes in the CONST file.
    :param data: the sanity data collected from scene. Dict from collectSanityData
    :return:
    """
    errors = []
    ignoreDefaultTransforms = ["|persp", "|top", "|front", "|side"]
    suffixes = [CONST.GROUP_SUFFIX['master']] + CONST.GROUP_SUFFIX['secondary']
    for eachXF in data['transform']:
        if eachXF not in ignoreDefaultTransforms:
            getChildren = cmds.listRelatives(eachXF, children = True, f = True)
            if not getChildren:
                if not validSuffix(suffixes, eachXF):
                    if eachXF not in errors:
                        errors.extend([eachXF])
            else:
                lookforshape = [shp for shp in getChildren if cmds.nodeType(shp) == 'mesh' or cmds.nodeType(shp) == 'nurbsCurve']
                if not lookforshape:
                    if not validSuffix(suffixes, eachXF):
                        if eachXF not in errors:
                            errors.extend([eachXF])
    return errors

def checkShapeNames(data):
    """
    Check for bad names
    :param data: the sanity data collected from scene. Dict from collectSanityData
    :return:
    """
    errors = []
    shapes =  data['nurbsCurve'] +  data['mesh']
    ## POLY MESH SHAPES
    for eachShape in shapes:
        if not cmds.getAttr('{}.intermediateObject'.format(eachShape)):
            ## Should end in shape
            if not eachShape.endswith('Shape'):
                if not eachShape in errors:
                    errors.extend([eachShape])

            ## Shape name should match transform name but with Shape on end the geo suffix
            parentName = cmds.listRelatives(eachShape, parent = True, f = True)[0]
            if "{}Shape".format(parentName.split("|")[-1]) != eachShape.split("|")[-1]:
                if not eachShape in errors:
                    errors.extend([eachShape])
    return errors

def checkSConstructionHistory(data):
    """
    Check for bad names
    :param data: the sanity data collected from scene. Dict from collectSanityData
    :return:
    """
    errors = []
    toCheck = data['mesh'] + data['nurbsCurve']
    for eachShape in toCheck:
        history = cmds.listHistory(eachShape, pdo = True, il = 1, gl = True)
        if history:
            if not eachShape in errors:
                errors.extend([eachShape])
    return errors

def checkDeadUtilityNodes():
    ####################################################################################
    ## Checking for mtx nodes with no connections
    nodeTypes  = loadNodeData()['nodes']
    badNodes = []
    for nType in nodeTypes['matrix']:
        if nType != 'transform' and nType != 'nurbsCurve':
            nodes = cmds.ls(type=nType)
            if nodes:
                for eachNode in nodes:
                    messageConnections  = cmds.listConnections('%s.message' % eachNode, destination=True)
                    if messageConnections:
                        destConns = [conn for conn in cmds.listConnections(eachNode, destination = True) if conn not in messageConnections]
                    else:
                        destConns = cmds.listConnections(eachNode, destination = True)

                    if not destConns:
                        badNodes = badNodes + [eachNode]
                    elif destConns:
                        if len(destConns) == 1:
                            badNodes = badNodes + [eachNode]
    return badNodes

def checkUtilityNames():
    ####################################################################################
    ## Checking naming on reparents, decompose, and compose nodes
    types = loadNodeData()['nodes']['matrix']   ## {'clamp': ['cNode'], 'addDoubleLinear': ['cNode', 'ADLUTL'], 'unitConversion': ['UC', 'cNode']}
    errors = []
    for nType, validSuffixes in types.items():
        if nType != 'transform' and nType != 'nurbsCurve':
            getAll = cmds.ls(type = nType)
            if getAll:
                for eachNode in getAll:
                    if not validSuffix(validSuffixes, eachNode):
                        errors.extend([eachNode])
    return errors

def validSuffix(suffixList, nodeName):
    suffixFound = False
    for eachSuffix in suffixList:
        if nodeName.endswith(eachSuffix):
            suffixFound = True
    return suffixFound

def checkNurbsCurves(data):
    """
    Check for bad names on nurbs Curvers
    :param data: the sanity data collected from scene. Dict from collectSanityData
    :return:
    """
    errors = []
    suffixes = CONST.NURBSCRV_SUFFIX['master'] + CONST.NURBSCRV_SUFFIX['secondary']
    for eachCrv in data['nurbsCurve']:
        p = cmds.listRelatives(eachCrv, p = True, f = True)[0]
        if not validSuffix(suffixes, eachCrv):
            if not p in errors:
                errors.extend([p])
    return errors

def checkDuplicateNames(data):
    errors = []
    for eachNode in list(set(data['duplicateNames'])):
        if data['duplicateNames'].count(eachNode) > 1:
            errors.extend([eachNode])
        elif "|" in eachNode:
            errors.extend([eachNode])

    return errors

def sanityCheck():
    """
    Used to process any of the sanity data:
    eg the groupNames and shapeNames need to be run through a proper check as the collectSanityData is just returning
    scene data collected without performing any kind of check.
    :return:
    """
    data = collectSanityData()
    sanitydata = {}

    ## Check duplicate names
    sanitydata['duplicateNames'] = checkDuplicateNames(data)

    ## Check shape names
    sanitydata['shapeNames'] = checkShapeNames(data)

    ## Geo Suffix
    sanitydata['geoSuffix'] = checkSuffix(data['mesh'], [CONST.GEOMETRY_SUFFIX['master']] + CONST.GEOMETRY_SUFFIX['secondary'], True, True)

    ## Joint Suffix
    sanitydata['joint'] = checkSuffix(data['joint'], [CONST.JOINT_SUFFIX['master']] + CONST.JOINT_SUFFIX['secondary'], False, False)

    ## NURBScurve Suffix
    sanitydata['nurbsCurve'] = checkSuffix(data['nurbsCurve'], [CONST.NURBSCRV_SUFFIX['master']] + CONST.NURBSCRV_SUFFIX['secondary'], True, True)

    ## Group Suffix
    sanitydata['grpSuffix'] = checkGrpSuffix(data)

    ## Reference nodes
    sanitydata['references'] = data['reference']

    ## Animation curves
    sanitydata['animCurves'] = data['animCurveTA'] + data['animCurveTL'] + data['animCurveTU']

    ## Intermediates
    sanitydata['intermediateObject'] = data['intermediateObject']

    ## TransformGeo
    sanitydata['transformGeometry'] = data["transformGeometry"]

    ## Dead Utility Nodes
    sanitydata['DeadUtility'] = checkDeadUtilityNodes()

    ## Bad MTX Names
    sanitydata['UtilityNames'] = checkUtilityNames()

    ## Nodes ending with a number!
    sanitydata['endingWith##'] = data["endingWith##"]

    ## pastedNodes
    sanitydata['pastedNodes'] = data["pastedNodes"]

    ## unknown
    sanitydata['unknown'] = data["unknown"]

    ## Construction history on nurbs curvs and meshes
    sanitydata['constructionHistory'] = checkSConstructionHistory(data)

    ## NonManifold ??

    ## Reversed Normals ??


    return sanitydata

