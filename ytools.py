# ================================================== 
# Imports
# ================================================== 

import bpy
import bmesh
import math
import mathutils

# ================================================== 
# bl_info
# ================================================== 

bl_info = {
    "name": "Y Tools",
    "category": "Mesh",
}

# ================================================== 
# constants
# ================================================== 

X_AXIS_INDEX = 0
Y_AXIS_INDEX = 1
Z_AXIS_INDEX = 2

# ================================================== 
# Operators
# ================================================== 

class YToolsAlignX(bpy.types.Operator):
    bl_idname = "mesh.ytools_align_x"
    bl_label = "Align To Active On X Axis"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        align_to_active(self, context, X_AXIS_INDEX)
        return {'FINISHED'}

class YToolsAlignY(bpy.types.Operator):
    bl_idname = "mesh.ytools_align_y"
    bl_label = "Align To Active On Y Axis"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        align_to_active(self, context, Y_AXIS_INDEX)
        return {'FINISHED'}

class YToolsAlignZ(bpy.types.Operator):
    bl_idname = "mesh.ytools_align_z"
    bl_label = "Align To Active On Z Axis"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        align_to_active(self, context, Z_AXIS_INDEX)
        return {'FINISHED'}

class YToolsAlignH(bpy.types.Operator):
    bl_idname = "mesh.ytools_align_horizontal"
    bl_label = "Align To Active Horizontally (On Both X and Y Axis)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        align_to_active(self, context, X_AXIS_INDEX)
        align_to_active(self, context, Y_AXIS_INDEX)
        return {'FINISHED'}

class YToolsAlignViewToFace(bpy.types.Operator):
    bl_idname = "view3d.align_view_to_active_face_normal"
    bl_label = "Align 3d View To Active Face Normal"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # print(type(context.space_data.region_3d.perspective_matrix))
        align_view_to_face(self, context)
        return {'FINISHED'}
    
# ================================================== 
# Registration
# ================================================== 

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()


# ================================================== 
# Functions
# ==================================================

def align_view_to_face(operator, context):
    mode = context.active_object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    try:
        region = context.space_data.region_3d
        matrix = context.space_data.region_3d.view_matrix
        rot = context.space_data.region_3d.view_rotation
        face = context.active_object.data.polygons.active
        normal = context.active_object.data.polygons[face].normal.copy()
    except AttributeError:
        operator.report({'ERROR'}, 'Attribute Error')
        bpy.ops.object.mode_set(mode=mode)
        return

    normal = -normal
    quat = normal.to_track_quat('-Z', 'Y')
    context.space_data.region_3d.view_rotation = quat
    bpy.ops.object.mode_set(mode=mode)


def align_to_active(operator, context, axis_index):
    mode = context.active_object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    verts = find_selected_vertices(context)
    if (len(verts) == 0):
        # operator.report({'ERROR'}, 'No vertices selected.')
        bpy.ops.object.mode_set(mode=mode)
        return

    snap_target = get_snap_target(context, axis_index)

    if snap_target == None:
        # operator.report({'ERROR'}, 'Nothing active to snap to.')
        bpy.ops.object.mode_set(mode=mode)
        return

    for vert in verts:
        vert.co[axis_index] = snap_target

    bpy.ops.object.mode_set(mode=mode)

def get_snap_target(context, axis_index):
    bm = bmesh.new()
    bm.from_mesh(context.object.data)
    # bm = bmesh.from_edit_mesh(context.object.data) 

    snap_target = None
    
    if not bm.select_history:
        bm.free()
        return None

    vert = bm.select_history[-1]
    if isinstance(vert, bmesh.types.BMVert):
        snap_target = vert.co[axis_index]

    if snap_target == None:
        face = bm.select_history[-1]
        if isinstance(face, bmesh.types.BMFace):
            center = face.calc_center_median()
            snap_target = center[axis_index]

    if snap_target == None:
        edge = bm.select_history[-1]
        if isinstance(edge, bmesh.types.BMEdge):
            pos1 = edge.verts[0].co
            pos2 = edge.verts[1].co
            midpoint = pos1.lerp(pos2, 0.5)
            snap_target = midpoint[axis_index]

    bm.free()
    return snap_target

def find_selected_vertices(context):
    return [v for v in context.active_object.data.vertices if v.select]

def get_selected_face_normal(context):
    context.scene.update()
    print(context.object.data.polygons.active)
    bm = bmesh.new()
    bm.from_mesh(context.object.data)

    bm.normal_update()

    if bm.select_history:
        face = bm.select_history[-1]
        if isinstance(face, bmesh.types.BMFace):
            result = face.normal.copy()
            bm.free()
            return result

    bm.free()
    return None
