# ================================================== 
# Imports
# ================================================== 

import bpy
import bmesh
import math

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

def align_to_active(operator, context, axis_index):
    mode = context.active_object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    verts = find_selected_vertices(context)
    if (len(verts) == 0):
        # operator.report({'ERROR'}, 'No vertices selected.')
        bpy.ops.object.mode_set(mode=mode)
        return

    snap_target = snap_target_from_active_vertex(context, axis_index)
    if snap_target == None && 
    if snap_target == None:
        # operator.report({'ERROR'}, 'No vertex selected to snap to.')
        bpy.ops.object.mode_set(mode=mode)
        return

    for vert in verts:
        vert.co[axis_index] = snap_target

    bpy.ops.object.mode_set(mode=mode)

def snap_target_from_active_vertex(context, axis_index):
    bm = bmesh.new()
    bm.from_mesh(context.object.data)
    # bm = bmesh.from_edit_mesh(context.object.data) 

    snap_target = None
    
    if bm.select_history:
        vert = bm.select_history[-1]
        if isinstance(vert, bmesh.types.BMVert):
            snap_target = vert.co[axis_index]

    bm.free()
    return snap_target

def find_selected_vertices(context):
    return [v for v in context.active_object.data.vertices if v.select]