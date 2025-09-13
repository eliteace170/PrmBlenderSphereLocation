import bpy

bl_info = {
    "name": "HitSphere Location Panel",
    "author": "eliteace",
    "version": (1, 1, 0),
    "blender": (3, 0, 0),
    "category": "3D View",
    "description": "Add an Empty (Sphere) and view game-space coords from evaluated world transform (includes constraints)."
}

# --- Conversion helpers (Blender -> Game) ---
def to_game_x(x: float) -> int:
    # invert and shift decimal two places (×100), rounded to nearest int
    return int(round(-x * 100))

def to_game_y(y: float) -> int:
    return int(round(-y * 100))

def to_game_z(z: float) -> int:
    return int(round(z * 100))

def to_game_scale(s: float) -> int:
    # single-number scale; if non-uniform, we take the average magnitude
    return int(round(s * 100))

# --- Evaluated world transform (reflects constraints/parents) ---
def world_loc_and_scale(obj: bpy.types.Object, context):
    """
    Returns (location_vec, scalar_scale) using the evaluated depsgraph so
    constraints (e.g., Child Of) and parenting are included.
    """
    dg = context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(dg)
    mw = obj_eval.matrix_world
    loc = mw.to_translation()
    scl = mw.to_scale()
    # Convert possible non-uniform scale to one number (average magnitude).
    s = (abs(scl.x) + abs(scl.y) + abs(scl.z)) / 3.0
    return loc, s

# --- Operator: Add Empty (Sphere) ---
class OBJECT_OT_add_hitbox_empty(bpy.types.Operator):
    """Add a hitbox Empty (Sphere)"""
    bl_idname = "object.add_hitbox_empty"
    bl_label = "Add Hitbox Empty"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Add at 3D cursor in world space
        bpy.ops.object.empty_add(
            type='SPHERE',
            align='WORLD',
            location=context.scene.cursor.location
        )
        obj = context.active_object
        if obj:
            obj.name = "Hitbox_Empty"
        return {'FINISHED'}

# --- UI Panel ---
class VIEW3D_PT_hitbox_panel(bpy.types.Panel):
    """Panel in the 3D Viewport (N-panel)"""
    bl_label = "Hitbox Location"
    bl_idname = "VIEW3D_PT_hitbox_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PrmHitSphere'

    @classmethod
    def poll(cls, context):
        # Always show so you can add the Empty even with no selection
        return True

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        # Always-available button to add the Empty (Sphere)
        layout.operator("object.add_hitbox_empty", icon='SPHERE')

        layout.separator()

        if not obj:
            # Nothing selected—show a hint
            layout.label(text="Select an object to see game values.", icon='INFO')
            return

        # Use evaluated world space so constraints/parents are reflected
        loc, s = world_loc_and_scale(obj, context)

        col = layout.column(align=True)
        col.label(text=f"Active: {obj.name}", icon='OBJECT_DATA')
        col.separator()

        col.label(text="ATKHIT_OFFSET (rounded):")
        row = col.row()
        row.label(text=f"X: {to_game_x(loc.x)}")
        row = col.row()
        row.label(text=f"Y: {to_game_y(loc.y)}")
        row = col.row()
        row.label(text=f"Z: {to_game_z(loc.z)}")

        col.separator()
        col.label(text="Sphere Scale:")
        col.label(text=f"{to_game_scale(s)}")

# --- Registration ---
classes = (
    OBJECT_OT_add_hitbox_empty,
    VIEW3D_PT_hitbox_panel,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
