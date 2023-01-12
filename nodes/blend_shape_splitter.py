"""
This node splits the deltas between the baseMesh mesh attribute and the ones in the inputMeshes[] mesh array attribute
into L/R sided in the outputLMeshes[]/outputRMeshes[] mesh array attributes

The separation map could be shown in the option is set to false.
The blend range could be set with the blendable float attribute the node.
"""
# as there is no maya.OpenMaya import, there is no need to specify which is the API version
import maya.api.OpenMaya as om


def maya_useNewAPI():
    pass


# Class definition
class BlendShapeSplitter(om.MPxNode):
    # Node definition
    VENDOR = 'Kike'
    VERSION = '1.0'
    NODENAME = 'blendShapeSplitter'
    NODEID = om.MTypeId(0x00118382)

    def __init__(self):
        om.MPxNode.__init__(self)
        # utilities for to compute
        self.base_mesh_vtx_count = 0
        self.is_base_mesh_dirty = True
        self.is_falloff_area_dirty = True
        self.is_display_layer_dirty = True
        self.l_falloff_map = True
        self.r_falloff_map = True

    def setDependentsDirty(self, dirtyPlug, affectedPlugs):
        if dirtyPlug.partialName() == om.MFnAttribute(self.attr_falloff_area).shortName:
            self.is_falloff_area_dirty = True
        if dirtyPlug.partialName() == om.MFnAttribute(self.attr_display_falloff_map).shortName:
            self.is_display_layer_dirty = True
        if dirtyPlug.partialName() == om.MFnAttribute(self.attr_base_mesh).shortName:
            self.is_base_mesh_dirty = True
        if om.MFnAttribute(self.attr_input_meshes).shortName in dirtyPlug.partialName():
            # only the index
            index = dirtyPlug.logicalIndex()
            affectedPlugs.append(om.MPlug(self.thisMObject(), self.attr_output_l_meshes).elementByLogicalIndex(index))
            affectedPlugs.append(om.MPlug(self.thisMObject(), self.attr_output_r_meshes).elementByLogicalIndex(index))

    def compute(self, plug, data):
        if plug == self.attr_output_l_meshes or plug == self.attr_output_r_meshes:
            # get input data
            side = "L" if plug == self.attr_output_l_meshes else "R"
            mesh_index = plug.logicalIndex()
            base_mesh_handler = data.inputValue(self.attr_base_mesh)  # type: om.MDataHandle
            input_mesh_handler = data.inputArrayValue(
                self.attr_input_meshes).jumpToLogicalElement(mesh_index).inputValue()  # type: om.MDataHandle
            out_mesh_handler = data.outputValue(plug)  # type: om.MDataHandle

            # proceed with checks for optimization proposes
            base_mesh_fn = om.MFnMesh(base_mesh_handler.asMesh())
            falloff = data.inputValue(self.attr_falloff_area).asFloat()
            if self.is_base_mesh_dirty:
                self.create_falloff_map(base_mesh_fn, falloff)
                self.is_falloff_area_dirty = False
                self.is_base_mesh_dirty = False
                self.base_mesh_vtx_count = base_mesh_fn.numVertices

            input_mesh_vtx_count = om.MFnMesh(input_mesh_handler.asMesh()).numVertices
            if self.base_mesh_vtx_count != input_mesh_vtx_count:
                om.MGlobal.displayError(
                    "The inputMesh {} does not have the same vtx than the base mesh. Unable to evaluate {}\n".format(
                        mesh_index, plug))
                data.setClean(plug)
                return

            # operate with the proper side
            # get map operation
            if self.is_falloff_area_dirty:
                self.create_falloff_map(base_mesh_fn, falloff)
                self.is_falloff_area_dirty = False

            # set out mesh
            out_mesh = self.generate_shape(base_mesh_fn, om.MFnMesh(input_mesh_handler.asMesh()), side)
            # get vertex color
            if self.is_display_layer_dirty:
                if data.inputValue(self.attr_display_falloff_map).asBool():
                    valid_map = self.l_falloff_map if side == "L" else self.r_falloff_map
                    out_mesh.setVertexColor(om.MColorArray([om.MColor(elem, elem, elem) for elem in valid_map]))
                self.is_display_layer_dirty = False
            out_mesh_handler.copy(base_mesh_handler)
            out_mesh_handler.setMObject(out_mesh.object())
            data.setClean(plug)

        if plug == self.attr_output_l_transforms or plug == self.attr_output_r_transforms:
            side = "L" if plug == self.attr_output_l_transforms else "R"
            plug_index = plug.logicalIndex()
            # get bounding box
            base_mesh_handler = data.inputValue(self.attr_base_mesh)  # type: om.MDataHandle
            try:

                bbox = om.MFnMesh(base_mesh_handler.asMesh()).boundingBox()
                print (bbox)
            except:
                return

            width = 2
            height = 2
            tx = (width * (plug_index % 2) + width) * (-1 if side == "R" else 1)
            ty = height * (plug_index // 2)
            out_trn_handler = data.outputValue(plug)  # type: om.MDataHandle
            out_trn_handler.set3Double(tx, ty, 0)
            # set default transform
            data.setClean(plug)

    def create_falloff_map(self, mesh, falloff):
        self.l_falloff_map = []
        self.r_falloff_map = []
        for vtx in mesh.getPoints(om.MSpace.kObject):

            abs_x = abs(vtx.x)
            if abs_x >= falloff:
                default_weight = 1
            else:
                default_weight = abs_x / float(falloff)

            if vtx.x >= 0:
                self.l_falloff_map.append(default_weight)
                self.r_falloff_map.append(1 - default_weight)
            else:
                self.l_falloff_map.append(1 - default_weight)
                self.r_falloff_map.append(default_weight)

    def generate_shape(self, base, target, side):
        valid_map = self.l_falloff_map if side == "L" else "R"

        return target

    # Node creator
    @classmethod
    def nodeCreator(cls):
        return BlendShapeSplitter()

    # Node initializer
    @classmethod
    def initialize(cls):
        t_attr = om.MFnTypedAttribute()
        n_attr = om.MFnNumericAttribute()

        # Input
        cls.attr_base_mesh = t_attr.create(
            "baseMesh", "baseMesh", om.MFnMeshData.kMesh)  # type: om.MFnTypedAttribute
        t_attr.storable = True
        cls.attr_input_meshes = t_attr.create(
            "inputMeshes", "inputMeshes", om.MFnMeshData.kMesh)  # type: om.MFnTypedAttribute
        t_attr.storable = True
        t_attr.array = True
        cls.attr_display_falloff_map = n_attr.create(
            "displayFalloffMap", "displayFalloffMap", om.MFnNumericData.kBoolean)  # type: om.MFnNumericAttribute
        n_attr.storable = True
        n_attr.channelBox = True
        cls.attr_falloff_area = n_attr.create(
            "falloffArea", "falloffArea", om.MFnNumericData.kFloat)  # type: om.MFnNumericAttribute
        n_attr.storable = True
        n_attr.channelBox = True
        n_attr.default = 0.5
        n_attr.setMin(0)
        cls.attr_row_meshes_number = n_attr.create(
            "rowMeshes", "rowMeshes", om.MFnNumericData.kInt)  # type: om.MFnNumericAttribute
        n_attr.storable = True
        n_attr.channelBox = True
        n_attr.default = 0
        n_attr.setMin(0)

        # Output
        cls.attr_output_l_meshes = t_attr.create(
            "outputLMeshes", "outputLMeshes", om.MFnMeshData.kMesh)  # type: om.MFnTypedAttribute
        t_attr.writable = False
        t_attr.storable = False
        t_attr.array = True
        cls.attr_output_r_meshes = t_attr.create(
            "outputRMeshes", "outputRMeshes", om.MFnMeshData.kMesh)  # type: om.MFnTypedAttribute
        t_attr.writable = False
        t_attr.storable = False
        t_attr.array = True
        cls.attr_output_l_transforms = n_attr.create(
            "outputLTransforms", "outputLTransforms", om.MFnNumericData.k3Double)  # type: om.MFnNumericAttribute
        n_attr.writable = False
        n_attr.storable = False
        n_attr.array = True
        cls.attr_output_r_transforms = n_attr.create(
            "outputRTransforms", "outputRTransforms", om.MFnNumericData.k3Double)  # type: om.MFnNumericAttribute
        n_attr.writable = False
        n_attr.storable = False
        n_attr.array = True

        # Setup node attributes
        cls.addAttribute(cls.attr_base_mesh)
        cls.addAttribute(cls.attr_input_meshes)
        cls.addAttribute(cls.attr_display_falloff_map)
        cls.addAttribute(cls.attr_falloff_area)
        cls.addAttribute(cls.attr_row_meshes_number)
        cls.addAttribute(cls.attr_output_l_meshes)
        cls.addAttribute(cls.attr_output_r_meshes)
        cls.addAttribute(cls.attr_output_l_transforms)
        cls.addAttribute(cls.attr_output_r_transforms)
        cls.attributeAffects(cls.attr_base_mesh, cls.attr_output_l_meshes)
        cls.attributeAffects(cls.attr_base_mesh, cls.attr_output_r_meshes)
        cls.attributeAffects(cls.attr_falloff_area, cls.attr_output_l_meshes)
        cls.attributeAffects(cls.attr_falloff_area, cls.attr_output_r_meshes)
        cls.attributeAffects(cls.attr_display_falloff_map, cls.attr_output_l_meshes)
        cls.attributeAffects(cls.attr_display_falloff_map, cls.attr_output_r_meshes)
        cls.attributeAffects(cls.attr_row_meshes_number, cls.attr_output_l_transforms)
        cls.attributeAffects(cls.attr_row_meshes_number, cls.attr_output_r_transforms)
        cls.attributeAffects(cls.attr_base_mesh, cls.attr_output_l_transforms)
        cls.attributeAffects(cls.attr_base_mesh, cls.attr_output_r_transforms)


# Initialize the scripted plug-in
def initializePlugin(mobject):
    mplugin = om.MFnPlugin(mobject, BlendShapeSplitter.VENDOR, BlendShapeSplitter.VERSION)
    try:
        mplugin.registerNode(
            BlendShapeSplitter.NODENAME,
            BlendShapeSplitter.NODEID,
            BlendShapeSplitter.nodeCreator,
            BlendShapeSplitter.initialize)
    except Exception:
        om.MGlobal.displayError("Failed to register node: " + BlendShapeSplitter.NODENAME)
        raise


# Uninitialize the scripted plug-in
def uninitializePlugin(mobject):
    mplugin = om.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(BlendShapeSplitter.NODEID)
    except Exception:
        om.MGlobal.displayError("Failed to deregister node: " + BlendShapeSplitter.NODENAME)
        raise
