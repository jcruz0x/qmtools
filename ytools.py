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

valid_texkeys = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '0'}

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
# globals
# ================================================== 

addon_keymaps = []
stored_images = {}

# ================================================== 
# Menu
# ================================================== 

class YToolsMenu(bpy.types.Menu):
    bl_label = "Y Tools Menu"
    bl_idname = "view3d.ytools_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'

        layout.operator("mesh.ytools_align_x")
        layout.operator("mesh.ytools_align_y")
        layout.operator("mesh.ytools_align_z")
        layout.operator("mesh.ytools_align_horizontal")
        layout.operator("view3d.align_view_to_active_face_normal")
        layout.operator("uv.quick_cubemap")
        layout.operator("uv.quick_cubemap_half")
        layout.operator("uv.quick_cubemap_modal")
        layout.operator("mesh.pick_image")
        layout.operator("mesh.assign_stored_image")
        layout.operator("mesh.linked_similar_image")
        layout.operator("mesh.toggle_backfaces")
        layout.operator("mesh.toggle_edge_length")
        layout.operator("mesh.split", text="Rip Faces")

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
    bl_label = "Align Both X and Z Axis To Active"
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

class YToolsQuickSimilarImage(bpy.types.Operator):
    bl_idname = "mesh.quick_similar_image"
    bl_label = "Quick Select Same Image"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.mesh.select_similar(type='IMAGE', threshold=0.01)
        return {'FINISHED'}

class YToolsSelectLinkedFaceSameImage(bpy.types.Operator):
    bl_idname = "mesh.linked_similar_image"
    bl_label = "Selected Linked Faces With Same Image"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        select_linked_with_same_image(self, context)
        return {'FINISHED'}

class YToolsToggleBackfaces(bpy.types.Operator):
    bl_idname = "mesh.toggle_backfaces"
    bl_label = "Backfaces Toggle"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.space_data.show_backface_culling ^= True
        return {'FINISHED'}

class YToolsToggleEdgeLength(bpy.types.Operator):
    bl_idname = "mesh.toggle_edge_length"
    bl_label = "Length Of Edges Toggle"
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context):
        context.object.data.show_extra_edge_length ^= True
        return {'FINISHED'}

class YToolsQuickCubeMapModal(bpy.types.Operator):
    bl_idname = "uv.quick_cubemap_modal"
    bl_label = "Cubeproject Modal"
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):
        context.area.header_text_set("CUBE PROJECTION: Select Cubemap Scale [1: 0.25]  [2: 0.5]  [3: 0.75]  [4: 1.0]  [5: 1.25]  [6: 1.5]  [7: 1.75]  [8: 2.0]  [9: 2.25]  [0: 2.5]")
        if event.unicode in cubemap_scales.keys():
            bpy.ops.uv.cube_project(cube_size = cubemap_scales[event.unicode])
            context.area.header_text_set()
            return {'FINISHED'}

        if event.type == 'ESC':
            context.area.header_text_set()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

class YToolsPickImageModal(bpy.types.Operator):
    bl_idname = "mesh.pick_image"
    bl_label = "Pick And Store Image"
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):
        context.area.header_text_set("PICK IMAGE: Select slot (0-9) to store image in.")
        if event.unicode in valid_texkeys:
            stored_images[event.unicode] = get_active_face_image_name(self, context)
            context.area.header_text_set()
            return {'FINISHED'}

        if event.type == 'ESC':
            context.area.header_text_set()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        # stored_images[0] = get_active_face_image_name(self, context)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

class YToolsAssignImageModal(bpy.types.Operator):
    bl_idname = "mesh.assign_stored_image"
    bl_label = "Texture Assign From Stored Image"
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):
        context.area.header_text_set("ASSIGN IMAGE: Select slot (0-9) to assign image from")
        if event.unicode in valid_texkeys:
            if event.unicode in stored_images.keys():
                assign_image_to_selected_faces_by_name(self, context, stored_images[event.unicode])
                context.area.header_text_set()
                return {'FINISHED'}
            else:
                context.area.header_text_set()
                return {'CANCELLED'}

        if event.type == 'ESC':
            context.area.header_text_set()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        # assign_image_to_selected_faces_by_name(self, context, stored_images[0])
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

# ================================================== 
# Registration
# ================================================== 

def register():
    bpy.utils.register_module(__name__)
    # bpy.utils.register_class(YToolsMenu)
    # bpy.ops.wm.call_menu(name=YToolsMenu.bl_idname)

    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name="Mesh")

    kmi = km.keymap_items.new('wm.call_menu', 'Y', 'PRESS')
    kmi.properties.name = YToolsMenu.bl_idname

    km.keymap_items.new(YToolsAlignZ.bl_idname, 'Z', 'PRESS', ctrl=True, shift=True)
    km.keymap_items.new(YToolsAlignX.bl_idname, 'X', 'PRESS', ctrl=True, shift=True)
    km.keymap_items.new(YToolsAlignY.bl_idname, 'C', 'PRESS', ctrl=True, shift=True)
    km.keymap_items.new(YToolsQuickCubeMap.bl_idname, 'Q', 'PRESS', ctrl=True, shift=True)
    km.keymap_items.new(YToolsQuickCubeMapHalf.bl_idname, 'W', 'PRESS', ctrl=True, shift=True)
    km.keymap_items.new(YToolsQuickSimilarImage.bl_idname, 'A', 'PRESS', ctrl=True, shift=True)
    km.keymap_items.new(YToolsSelectLinkedFaceSameImage.bl_idname, 'F', 'PRESS', ctrl=True, shift=True)

    addon_keymaps.append(km)

def unregister():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()

    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()

# ================================================== 
# Functions
# ==================================================

def select_linked_with_same_image(operator, context):

    mode = context.active_object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    bm = bmesh.new()
    bm.from_mesh(context.object.data) 

    bm.faces.ensure_lookup_table()
    tex_lay = bm.faces.layers.tex.active

    face_list = [f for f in bm.faces if f.select]

    if len(face_list) == 0:
        # operator.report({'ERROR'}, 'No faces selected.')
        bm.free()
        bpy.ops.object.mode_set(mode=mode)
        return

    if bm.select_history:
        elem = bm.select_history[-1]
        active_face_index = elem.index if isinstance(elem, bmesh.types.BMFace) else face_list[0].index
        active_image_name = bm.faces[active_face_index][tex_lay].image.name
    else:
        bpy.ops.object.mode_set(mode=mode)
        bm.free()
        return

    final_selection = set()
    while face_list:
        new_faces = []
        for face in face_list:
            if face.index in final_selection:
                continue
            if face[tex_lay].image.name != active_image_name:
                continue
            final_selection.add(face.index) 
            for edge in face.edges:
               linked = edge.link_faces
               for face in linked:
                   new_faces.append(face)
        face_list = new_faces if len(new_faces) > 0 else None 

    for face_index in final_selection:
        context.active_object.data.polygons[face_index].select = True

    bpy.ops.object.mode_set(mode=mode)
    bm.free()

def get_active_face_image_name(operator, context):
    mode = context.active_object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    faceno = context.active_object.data.polygons.active
    face = context.active_object.data.uv_textures.active.data[faceno]

    print(face.image.name)

    name = face.image.name

    bpy.ops.object.mode_set(mode=mode)

    return name

def assign_image_to_selected_faces_by_name(operator, context, name):
    mode = context.active_object.mode
    bpy.ops.object.mode_set(mode='OBJECT')

    for img in bpy.data.images:
        if img.name == name:
            image_to_assign = img
            break
    else:
        return False

    selected_faces = [f for f in context.active_object.data.polygons if f.select]

    for face in selected_faces:
      context.active_object.data.uv_textures.active.data[face.index].image = image_to_assign

    bpy.ops.object.mode_set(mode=mode)

    return True

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
