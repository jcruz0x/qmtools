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
# constants / data
# ================================================== 

X_AXIS_INDEX = 0
Y_AXIS_INDEX = 1
Z_AXIS_INDEX = 2

cubemap_scales = {
    '1': 0.25,
    '2': 0.5, 
    '3': 0.75, 
    '4': 1.0, 
    '5': 1.25, 
    '6': 1.5, 
    '7': 1.75, 
    '8': 2.0, 
    '9': 2.25, 
    '0': 2.5,
    'u': 1.0,
    'i': 0.5,
}

# ================================================== 
# Menu
# ================================================== 

class YToolsMenu(bpy.types.Menu):
    bl_label = "Y Tools Menu"
    bl_idname = "view3d.ytools_menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("mesh.ytools_align_x")
        layout.operator("mesh.ytools_align_y")
        layout.operator("mesh.ytools_align_z")
        layout.operator("mesh.ytools_align_h")
        layout.operator("view3d.align_view_to_active_face_normal")
        layout.operator("uv.quick_cubemap")
        layout.operator("uv.quick_cubemap_half")
        layout.operator("uv.quick_cubemap_modal")
        layout.operator("mesh.split")

# ================================================== 
# Operators
# ================================================== 

class YToolsAlignX(bpy.types.Operator):
    bl_idname = "mesh.ytools_align_x"
    bl_label = "X Axis Align To Active"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        align_to_active(self, context, X_AXIS_INDEX)
        return {'FINISHED'}

class YToolsAlignY(bpy.types.Operator):
    bl_idname = "mesh.ytools_align_y"
    bl_label = "Y Axis Align To Active"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        align_to_active(self, context, Y_AXIS_INDEX)
        return {'FINISHED'}

class YToolsAlignZ(bpy.types.Operator):
    bl_idname = "mesh.ytools_align_z"
    bl_label = "Z Axis Align To Active"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        align_to_active(self, context, Z_AXIS_INDEX)
        return {'FINISHED'}

class YToolsAlignH(bpy.types.Operator):
    bl_idname = "mesh.ytools_align_horizontal"
    bl_label = "Horizontal Align To Active"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        align_to_active(self, context, X_AXIS_INDEX)
        align_to_active(self, context, Y_AXIS_INDEX)
        return {'FINISHED'}

class YToolsAlignViewToFace(bpy.types.Operator):
    bl_idname = "view3d.align_view_to_active_face_normal"
    bl_label = "Face Normal Aligned 3D View"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # print(type(context.space_data.region_3d.perspective_matrix))
        align_view_to_face(self, context)
        return {'FINISHED'}

class YToolsQuickCubeMapModal(bpy.types.Operator):
    bl_idname = "uv.quick_cubemap_modal"
    bl_label = "Cubeproject Modal"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self):
        print("Quick UVMapper Start")

    def __del__(self):
        print("Quick UVMapper End")

    def modal(self, context, event):
        if event.unicode in cubemap_scales.keys():
            bpy.ops.uv.cube_project(cube_size = cubemap_scales[event.unicode])
            return {'FINISHED'}

        if event.type == 'ESC':
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        print(context.window_manager.modal_handler_add(self))
        return {'RUNNING_MODAL'}
    
class YToolsQuickCubeMap(bpy.types.Operator):
    bl_idname = "uv.quick_cubemap"
    bl_label = "Unwrap Cubeproject" 
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.uv.cube_project(cube_size = 1.0)
        return {'FINISHED'}

class YToolsQuickCubeMapHalf(bpy.types.Operator):
    bl_idname = "uv.quick_cubemap_half"
    bl_label = "Half Scale Cubeproject"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.uv.cube_project(cube_size = 0.5)
        return {'FINISHED'}

# ================================================== 
# Registration
# ================================================== 

def register():
    bpy.utils.register_module(__name__)
    bpy.ops.wm.call_menu(name=YToolsMenu.bl_idname)

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
