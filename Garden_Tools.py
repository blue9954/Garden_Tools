bl_info = {
    "name": "PG Rename",
    "author": "Gemini Code Assist",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Rename Tool",
    "description": "선택된 2개의 Mesh 폴리곤 수를 비교하여 _high, _low로 이름 변경 및 컬렉션 분리",
    "category": "Object",
}

import os
import math
import bmesh
import bpy


class OBJECT_OT_rename_high_low(bpy.types.Operator):
    bl_idname = "object.rename_high_low"
    bl_label = "Rename High/Low"
    bl_options = {'REGISTER', 'UNDO'}

    base_name: bpy.props.StringProperty(
        name="Base Name",
        description="적용할 기본 이름을 입력하세요",
        default="Asset"
    )
    
    is_valid: bpy.props.BoolProperty(default=True, options={'HIDDEN'})
    error_message: bpy.props.StringProperty(default="", options={'HIDDEN'})

    def invoke(self, context, event):
        selected = context.selected_objects
        
        # 검증 1: 정확히 2개 선택되었는가?
        if len(selected) != 2:
            self.is_valid = False
            self.error_message = "에러: 정확히 2개의 오브젝트를 선택해야 합니다."
            return context.window_manager.invoke_props_dialog(self)
            
        # 검증 2: 둘 다 Mesh 타입인가?
        if selected[0].type != 'MESH' or selected[1].type != 'MESH':
            self.is_valid = False
            self.error_message = "에러: 선택된 오브젝트는 모두 Mesh여야 합니다."
            return context.window_manager.invoke_props_dialog(self)

        # 검증 통과
        self.is_valid = True
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        if not self.is_valid:
            layout.label(text=self.error_message, icon='ERROR')
        else:
            layout.prop(self, "base_name")
            layout.label(text="확인을 누르면 _high 및 _low로 변경됩니다.")

    def execute(self, context):
        if not self.is_valid:
            return {'CANCELLED'}

        obj_a, obj_b = context.selected_objects
        
        # 폴리곤(면) 수 비교
        poly_a = len(obj_a.data.polygons)
        poly_b = len(obj_b.data.polygons)
        
        if poly_a >= poly_b:
            high_obj, low_obj = obj_a, obj_b
        else:
            high_obj, low_obj = obj_b, obj_a
            
        # 이름 변경
        high_obj.name = f"{self.base_name}_high"
        for slot in high_obj.material_slots:
            if slot.material:
                slot.material.name = f"{high_obj.name}_Mat"
                
        low_obj.name = f"{self.base_name}_low"
        for slot in low_obj.material_slots:
            if slot.material:
                slot.material.name = f"{low_obj.name}_Mat"
        
        # 컬렉션 생성 및 가져오기 헬퍼 함수
        def get_or_create_collection(name):
            if name in bpy.data.collections:
                return bpy.data.collections[name]
            new_col = bpy.data.collections.new(name)
            context.scene.collection.children.link(new_col)
            return new_col
            
        high_col = get_or_create_collection("High")
        low_col = get_or_create_collection("Low")
        
        # 오브젝트를 특정 컬렉션으로 이동시키는 헬퍼 함수
        def move_to_collection(obj, target_col):
            if obj.name not in target_col.objects:
                target_col.objects.link(obj)
            # 기존 소속 컬렉션에서 링크 해제
            for col in obj.users_collection:
                if col != target_col:
                    col.objects.unlink(obj)
                    
        move_to_collection(high_obj, high_col)
        move_to_collection(low_obj, low_col)

        self.report({'INFO'}, f"성공: {high_obj.name}, {low_obj.name} 생성 완료")
        return {'FINISHED'}


class OBJECT_OT_rename_multi(bpy.types.Operator):
    bl_idname = "object.rename_multi"
    bl_label = "Multi Rename"
    bl_options = {'REGISTER', 'UNDO'}

    base_name: bpy.props.StringProperty(
        name="Base Name",
        description="적용할 기본 이름을 입력하세요",
        default="Asset"
    )
    
    is_valid: bpy.props.BoolProperty(default=True, options={'HIDDEN'})
    error_message: bpy.props.StringProperty(default="", options={'HIDDEN'})

    def invoke(self, context, event):
        meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        # 검증 1: 1개 이상의 Mesh가 선택되었는가?
        if len(meshes) < 1:
            self.is_valid = False
            self.error_message = "에러: 1개 이상의 Mesh 오브젝트를 선택해야 합니다."
            return context.window_manager.invoke_props_dialog(self)
            
        # 검증 통과
        self.is_valid = True
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        if not self.is_valid:
            layout.label(text=self.error_message, icon='ERROR')
        else:
            layout.prop(self, "base_name")
            layout.label(text="확인을 누르면 _01, _02... 순으로 변경됩니다.")

    def execute(self, context):
        if not self.is_valid:
            return {'CANCELLED'}

        meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        # 이름 알파벳순 정렬
        meshes.sort(key=lambda x: x.name)
        
        # 인덱스 계산 및 이름 변경
        for idx, obj in enumerate(meshes, start=1):
            obj.name = f"{self.base_name}_{idx:02d}"
            for slot in obj.material_slots:
                if slot.material:
                    slot.material.name = f"{obj.name}_Mat"
            
        self.report({'INFO'}, f"성공: {len(meshes)}개의 오브젝트 이름 변경 완료")
        return {'FINISHED'}


class OBJECT_OT_rename_materials(bpy.types.Operator):
    bl_idname = "object.rename_materials"
    bl_label = "Rename Material by Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected = context.selected_objects
        
        if not selected:
            self.report({'ERROR'}, "No object selected")
            return {'CANCELLED'}
            
        for obj in selected:
            # Mesh가 아니거나 Material Slot이 없는 경우, 에러로 종료하지 않고 스킵(continue)하여 다음 오브젝트 진행
            if obj.type != 'MESH' or not obj.material_slots:
                continue
                
            for slot in obj.material_slots:
                if slot.material:
                    # 다른 오브젝트와 머티리얼을 공유 중이라면 복제하여 각각 독립적인 이름을 가질 수 있도록 함
                    if slot.material.users > 1:
                        slot.material = slot.material.copy()
                        
                    slot.material.name = f"{obj.name}_Mat"
                    
        self.report({'INFO'}, "선택된 메쉬들의 머티리얼 이름 변경이 완료되었습니다.")
        return {'FINISHED'}


class OBJECT_OT_clean_up_meshes(bpy.types.Operator):
    """선택된 메쉬들을 정리합니다: Merge, Clean, Shade Smooth, Apply Transforms"""
    bl_idname = "object.clean_up_meshes"
    bl_label = "Clean Up"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # 오브젝트가 선택되었고, 그 중 하나라도 메쉬일 때만 버튼 활성화
        return context.selected_objects and any(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        # 0. 선택된 메쉬 오브젝트만 필터링
        mesh_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        # poll()에서 이미 확인했지만, 만약을 위해 한번 더 확인
        if not mesh_objects:
            self.report({'WARNING'}, "정리할 메쉬 오브젝트가 선택되지 않았습니다.")
            return {'CANCELLED'}

        # 현재 활성 오브젝트와 모드를 저장해두었다가 마지막에 복원
        active_obj = context.view_layer.objects.active
        original_mode = 'OBJECT'
        if active_obj:
            original_mode = active_obj.mode

        # 1, 2, 3번 작업을 각 메쉬에 대해 반복
        for obj in mesh_objects:
            # 작업을 위해 현재 오브젝트를 활성화
            context.view_layer.objects.active = obj
            
            # 1. Vertex merge & 2. Clean up (에디트 모드에서 실행)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=0.0001)
            bpy.ops.mesh.delete_loose()
            bpy.ops.mesh.dissolve_degenerate()
            bpy.ops.object.mode_set(mode='OBJECT')

        # 3. Apply Rotation & Scale (선택된 모든 메쉬에 한번에 적용)
        # 루프에서 선택 상태를 바꾸지 않았으므로, 원래 선택된 메쉬들에 적용됨
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        # 원래의 활성 오브젝트와 모드로 복원
        context.view_layer.objects.active = active_obj
        if active_obj and active_obj.mode != original_mode:
            try:
                bpy.ops.object.mode_set(mode=original_mode)
            except RuntimeError:
                # 모드 변경이 불가능한 경우 (예: 오브젝트가 사라짐) 오류를 무시
                pass

        self.report({'INFO'}, f"{len(mesh_objects)}개의 메쉬를 정리했습니다.")
        return {'FINISHED'}


class OBJECT_OT_export_low_fbx(bpy.types.Operator):
    bl_idname = "object.export_low_fbx"
    bl_label = "Export Low FBX"
    bl_options = {'REGISTER', 'UNDO'}

    is_valid: bpy.props.BoolProperty(default=True, options={'HIDDEN'})
    message: bpy.props.StringProperty(default="", options={'HIDDEN'})

    def invoke(self, context, event):
        # 1. .blend 파일 저장 여부 확인
        if not bpy.data.filepath:
            self.is_valid = False
            self.message = "에러: .blend 파일을 먼저 저장해야 합니다."
            return context.window_manager.invoke_props_dialog(self)

        # 2. _Low 접미사 메시 수집 (대소문자 구분 없이 _low로 끝나는지 검사)
        low_meshes = [obj for obj in context.scene.objects if obj.type == 'MESH' and obj.name.lower().endswith("_low")]
        
        if not low_meshes:
            self.is_valid = False
            self.message = "에러: 씬에 '_Low' (또는 '_low') 접미사가 붙은 Mesh가 없습니다."
            return context.window_manager.invoke_props_dialog(self)

        # 검증 통과 시
        self.is_valid = True
        self.message = f"총 {len(low_meshes)}개의 _Low 메시를 익스포트 하시겠습니까?"
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        if not self.is_valid:
            layout.label(text=self.message, icon='ERROR')
        else:
            layout.label(text=self.message, icon='INFO')

    def execute(self, context):
        if not self.is_valid:
            return {'CANCELLED'}

        blend_dir = os.path.dirname(bpy.data.filepath)
        fbx_dir = os.path.join(blend_dir, "FBX")
        os.makedirs(fbx_dir, exist_ok=True)

        low_meshes = [obj for obj in context.scene.objects if obj.type == 'MESH' and obj.name.lower().endswith("_low")]
        backup_locations = {obj: obj.location.copy() for obj in low_meshes}
        exported_count = 0

        for obj in low_meshes:
            # 메시를 원점으로 이동
            obj.location = (0.0, 0.0, 0.0)
            
            # 해당 메시만 단독 선택
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj

            # FBX 파일명 생성 (_Low 제거 후 .fbx 부착)
            base_name = obj.name[:-4] 
            fbx_path = os.path.join(fbx_dir, f"{base_name}.fbx")

            # 익스포트 시 내부 Mesh 이름도 _Low 제거
            original_name = obj.name
            obj.name = base_name

            # FBX 익스포트 실행
            bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True)
            exported_count += 1

            # 원본 이름 및 위치 복원
            obj.name = original_name
            obj.location = backup_locations[obj]

        # 완료 알림 팝업 함수
        def draw_popup(menu, context):
            menu.layout.label(text=f"익스포트된 파일 수: {exported_count}개")
            menu.layout.label(text=f"경로: {fbx_dir}")

        bpy.context.window_manager.popup_menu(draw_popup, title="FBX 익스포트 완료", icon='FILE_TICK')
        self.report({'INFO'}, f"성공: {exported_count}개 파일 익스포트 완료")
        return {'FINISHED'}


class VIEW3D_PT_rename_tool(bpy.types.Panel):
    bl_label = "Rename Panel"
    bl_idname = "VIEW3D_PT_rename_tool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Garden Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_rename_high_low.bl_idname, text="Rename High/Low", icon='OUTLINER_OB_MESH')
        layout.operator(OBJECT_OT_rename_multi.bl_idname, text="Multi Rename", icon='SORTALPHA')
        layout.operator(OBJECT_OT_rename_materials.bl_idname, text="Rename Material by Mesh", icon='MATERIAL')
        layout.operator(OBJECT_OT_clean_up_meshes.bl_idname, text="Clean Up", icon='BRUSH_DATA')
        layout.operator(OBJECT_OT_export_low_fbx.bl_idname, text="Export Low FBX", icon='EXPORT')


def _sg_apply_auto_smooth(obj, angle_rad):
    if obj.mode == 'EDIT':
        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        for face in bm.faces:
            face.smooth = True
        for edge in bm.edges:
            if len(edge.link_faces) == 2:
                f1, f2 = edge.link_faces
                dot = max(-1.0, min(1.0, f1.normal.dot(f2.normal)))
                edge.smooth = (math.acos(dot) <= angle_rad)
            else:
                edge.smooth = False
        bmesh.update_edit_mesh(obj.data)
    else:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        for face in bm.faces:
            face.smooth = True
        for edge in bm.edges:
            if len(edge.link_faces) == 2:
                f1, f2 = edge.link_faces
                dot = max(-1.0, min(1.0, f1.normal.dot(f2.normal)))
                edge.smooth = (math.acos(dot) <= angle_rad)
            else:
                edge.smooth = False
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()

    if hasattr(obj.data, 'use_auto_smooth'):
        obj.data.use_auto_smooth = True
        obj.data.auto_smooth_angle = angle_rad


def sg_auto_smooth_update(self, context):
    obj = context.active_object
    if obj is None or obj.type != 'MESH':
        return
    _sg_apply_auto_smooth(obj, math.radians(self.sg_auto_smooth_angle))


class OBJECT_OT_sg_clear_all(bpy.types.Operator):
    bl_idname = "object.sg_clear_all"
    bl_label = "Clear All"
    bl_description = "모든 메쉬의 노멀 데이터를 제거하고 Flat으로 초기화합니다"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        obj = context.active_object
        was_edit = obj.mode == 'EDIT'

        if not was_edit:
            bpy.ops.object.mode_set(mode='EDIT')

        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

        for face in bm.faces:
            face.smooth = False
        for edge in bm.edges:
            edge.smooth = True

        bmesh.update_edit_mesh(obj.data)

        try:
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
        except Exception:
            pass

        if hasattr(obj.data, 'use_auto_smooth'):
            obj.data.use_auto_smooth = False

        if not was_edit:
            bpy.ops.object.mode_set(mode='OBJECT')

        self.report({'INFO'}, "모든 노멀 데이터를 초기화했습니다.")
        return {'FINISHED'}


class OBJECT_OT_sg_select_clear(bpy.types.Operator):
    bl_idname = "object.sg_select_clear"
    bl_label = "Select Clear"
    bl_description = "선택한 Face 영역의 노멀을 제거하여 Flat하게 만듭니다"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        obj = context.active_object
        was_edit = obj.mode == 'EDIT'

        if not was_edit:
            bpy.ops.object.mode_set(mode='EDIT')

        bpy.ops.mesh.select_mode(use_extend=False, use_expand=True, type='FACE')

        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

        for face in bm.faces:
            if face.select:
                face.smooth = False

        for edge in bm.edges:
            if all(f.select for f in edge.link_faces) and edge.link_faces:
                edge.smooth = True

        bmesh.update_edit_mesh(obj.data)

        if not was_edit:
            bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}


class OBJECT_OT_sg_auto_smooth(bpy.types.Operator):
    bl_idname = "object.sg_auto_smooth"
    bl_label = "Auto Smooth"
    bl_description = "지정한 각도 이상의 Edge를 Sharp로 처리하여 Auto Smooth를 적용합니다"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        obj = context.active_object
        angle_deg = context.scene.sg_auto_smooth_angle
        _sg_apply_auto_smooth(obj, math.radians(angle_deg))
        self.report({'INFO'}, f"Auto Smooth {angle_deg:.1f}° 적용 완료")
        return {'FINISHED'}


class OBJECT_OT_sg_select_smooth(bpy.types.Operator):
    bl_idname = "object.sg_select_smooth"
    bl_label = "Select Smooth"
    bl_description = "선택된 Face의 외곽 Edge에 Sharp를 적용하고 내부를 Smooth 처리합니다"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        obj = context.active_object
        was_edit = obj.mode == 'EDIT'

        if not was_edit:
            bpy.ops.object.mode_set(mode='EDIT')

        bpy.ops.mesh.select_mode(use_extend=False, use_expand=True, type='FACE')

        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        bm.edges.ensure_lookup_table()

        for face in bm.faces:
            if face.select:
                face.smooth = True

        for edge in bm.edges:
            selected_count = sum(1 for f in edge.link_faces if f.select)
            if selected_count == 1:
                edge.smooth = False
            elif selected_count == 2:
                edge.smooth = True

        bmesh.update_edit_mesh(obj.data)

        if not was_edit:
            bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}


class VIEW3D_PT_smoothing_group(bpy.types.Panel):
    bl_label = "Smoothing Group"
    bl_idname = "VIEW3D_PT_smoothing_group"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Garden Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_sg_clear_all.bl_idname, text="Clear All", icon='NORMALS_VERTEX_FACE')
        layout.operator(OBJECT_OT_sg_select_clear.bl_idname, text="Select Clear", icon='NORMALS_VERTEX')
        row = layout.row(align=True)
        row.operator(OBJECT_OT_sg_auto_smooth.bl_idname, text="Auto Smooth", icon='SMOOTHCURVE')
        row.prop(context.scene, "sg_auto_smooth_angle", text="")
        layout.operator(OBJECT_OT_sg_select_smooth.bl_idname, text="Select Smooth", icon='ANTIALIASED')


def register():
    bpy.utils.register_class(OBJECT_OT_rename_high_low)
    bpy.utils.register_class(OBJECT_OT_rename_multi)
    bpy.utils.register_class(OBJECT_OT_rename_materials)
    bpy.utils.register_class(OBJECT_OT_clean_up_meshes)
    bpy.utils.register_class(OBJECT_OT_export_low_fbx)
    bpy.utils.register_class(VIEW3D_PT_rename_tool)
    bpy.utils.register_class(OBJECT_OT_sg_clear_all)
    bpy.utils.register_class(OBJECT_OT_sg_select_clear)
    bpy.utils.register_class(OBJECT_OT_sg_auto_smooth)
    bpy.utils.register_class(OBJECT_OT_sg_select_smooth)
    bpy.utils.register_class(VIEW3D_PT_smoothing_group)
    bpy.types.Scene.sg_auto_smooth_angle = bpy.props.FloatProperty(
        name="Angle",
        default=45.0,
        min=0.0,
        max=180.0,
        precision=1,
        step=100,
        update=sg_auto_smooth_update,
    )

def unregister():
    del bpy.types.Scene.sg_auto_smooth_angle
    bpy.utils.unregister_class(VIEW3D_PT_smoothing_group)
    bpy.utils.unregister_class(OBJECT_OT_sg_select_smooth)
    bpy.utils.unregister_class(OBJECT_OT_sg_auto_smooth)
    bpy.utils.unregister_class(OBJECT_OT_sg_select_clear)
    bpy.utils.unregister_class(OBJECT_OT_sg_clear_all)
    bpy.utils.unregister_class(VIEW3D_PT_rename_tool)
    bpy.utils.unregister_class(OBJECT_OT_export_low_fbx)
    bpy.utils.unregister_class(OBJECT_OT_clean_up_meshes)
    bpy.utils.unregister_class(OBJECT_OT_rename_materials)
    bpy.utils.unregister_class(OBJECT_OT_rename_multi)
    bpy.utils.unregister_class(OBJECT_OT_rename_high_low)


if __name__ == "__main__":
    register()
