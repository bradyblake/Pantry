#Author: Claude (generated for Brady's pantry project)
#Description: Pantry Pull-Out Shelf Frame - Fusion 360 Python Script v5
#
# CORRECTED VERSION:
# - 14 gauge 1.5" square tube
# - Top cross braces sit ON TOP of verticals (caps open ends)
# - Verticals: 82.5" (84" - 1.5" for top brace)
# - Cross braces: 32.5" (fit between V1 and V3)
# - Stretchers: 33" (front to back)
# - All open tube ends face walls/ceiling
#
# HOW TO USE:
# 1. Open Fusion 360
# 2. Go to Tools > Add-Ins > Scripts and Add-Ins (or press Shift+S)
# 3. Click the green "+" next to "My Scripts"
# 4. Create a new script, name it "PantryFrame"
# 5. Replace the generated code with this file's contents
# 6. Click "Run"

import adsk.core, adsk.fusion, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct
        rootComp = design.rootComponent
        
        # ============================================
        # CONFIGURATION
        # ============================================
        
        def inch(inches):
            """Convert inches to centimeters for Fusion 360"""
            return inches * 2.54
        
        # Overall dimensions
        TOTAL_WIDTH = inch(35.5)
        TOTAL_DEPTH = inch(36)
        TOTAL_HEIGHT = inch(84)      # Top of frame (verticals + top brace)
        
        # Steel tube (14 gauge)
        TUBE = inch(1.5)
        
        # Vertical height (top brace sits on top)
        VERTICAL_HEIGHT = inch(82.5)  # 84" - 1.5" = 82.5"
        
        # ============================================
        # WIDTH BREAKDOWN (35.5" total)
        # ============================================
        # | V1 | LEFT COLUMN | V2 | SPICE + ICE MAKER | V3 |
        # | 1.5|     10      |1.5 |        21         |1.5 | = 35.5" ✓
        
        LEFT_COL_CLEAR = inch(10)        # Clear opening for left shelves
        SPICE_CLEAR = inch(5)            # Clear width for spice tower
        ICE_MAKER_CLEAR = inch(15)       # Clear width for ice maker
        RIGHT_AREA_CLEAR = inch(21)      # Combined spice + ice maker area
        
        # ============================================
        # VERTICAL POSITIONS (X-axis)
        # ============================================
        
        V1_X = 0                                    # Left edge
        V2_X = TUBE + LEFT_COL_CLEAR                # 1.5 + 10 = 11.5"
        V3_X = TOTAL_WIDTH - TUBE                   # 35.5 - 1.5 = 34"
        
        # Depth positions
        FRONT_Y = 0
        BACK_Y = TOTAL_DEPTH - TUBE
        
        # Stretcher length (front to back, between posts)
        STRETCHER_LEN = TOTAL_DEPTH - (2 * TUBE)   # 36 - 3 = 33"
        
        # Cross brace length (between V1 and V3)
        CROSS_BRACE_LEN = V3_X - V1_X - TUBE       # 34 - 0 - 1.5 = 32.5"
        
        # ============================================
        # HEIGHT LEVELS
        # ============================================
        
        # Left column: 5 shelf levels
        LEFT_HEIGHTS = [inch(2), inch(16), inch(30), inch(44), inch(58)]
        
        # Upper right (above ice maker): 4 shelf levels
        ICE_MAKER_TOP = inch(34)
        UPPER_HEIGHTS = [inch(38), inch(50), inch(62), inch(74)]
        
        # Cross brace heights
        BOTTOM_BRACE_Z = 0
        MID_BRACE_Z = ICE_MAKER_TOP                # 34"
        # Top brace sits ON TOP of verticals at 82.5"
        
        # ============================================
        # HELPER FUNCTION
        # ============================================
        
        def create_box(comp, name, x, y, z, width, depth, height):
            """Create a solid box at position (x,y,z) with given dimensions"""
            sketches = comp.sketches
            xyPlane = comp.xYConstructionPlane
            sketch = sketches.add(xyPlane)
            
            lines = sketch.sketchCurves.sketchLines
            lines.addTwoPointRectangle(
                adsk.core.Point3D.create(x, y, 0),
                adsk.core.Point3D.create(x + width, y + depth, 0)
            )
            
            prof = sketch.profiles.item(0)
            
            extrudes = comp.features.extrudeFeatures
            extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            
            startOffset = adsk.fusion.OffsetStartDefinition.create(adsk.core.ValueInput.createByReal(z))
            extInput.startExtent = startOffset
            
            distance = adsk.core.ValueInput.createByReal(height)
            extInput.setDistanceExtent(False, distance)
            ext = extrudes.add(extInput)
            
            if ext.bodies.count > 0:
                ext.bodies.item(0).name = name
            return ext
        
        # ============================================
        # CREATE COMPONENTS
        # ============================================
        
        frameOcc = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        frameComp = frameOcc.component
        frameComp.name = "Steel_Frame"
        
        shelfOcc = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        shelfComp = shelfOcc.component
        shelfComp.name = "Shelves"
        
        spiceOcc = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        spiceComp = spiceOcc.component
        spiceComp.name = "Spice_Tower"
        
        iceOcc = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        iceComp = iceOcc.component
        iceComp.name = "Ice_Maker_Platform"
        
        # ============================================
        # VERTICALS (6 total: 3 positions × front/back)
        # Height: 82.5" (top brace sits on top)
        # ============================================
        
        # V1 - Left edge
        create_box(frameComp, "V1_Front", V1_X, FRONT_Y, 0, TUBE, TUBE, VERTICAL_HEIGHT)
        create_box(frameComp, "V1_Back", V1_X, BACK_Y, 0, TUBE, TUBE, VERTICAL_HEIGHT)
        
        # V2 - Between left column and right area
        create_box(frameComp, "V2_Front", V2_X, FRONT_Y, 0, TUBE, TUBE, VERTICAL_HEIGHT)
        create_box(frameComp, "V2_Back", V2_X, BACK_Y, 0, TUBE, TUBE, VERTICAL_HEIGHT)
        
        # V3 - Right edge
        create_box(frameComp, "V3_Front", V3_X, FRONT_Y, 0, TUBE, TUBE, VERTICAL_HEIGHT)
        create_box(frameComp, "V3_Back", V3_X, BACK_Y, 0, TUBE, TUBE, VERTICAL_HEIGHT)
        
        # ============================================
        # CROSS BRACES (run left to right)
        # Bottom and mid: fit between verticals
        # Top: sit ON TOP of verticals (cap the open ends)
        # ============================================
        
        # Bottom braces (front and back) - between verticals
        create_box(frameComp, "Brace_Bot_Front", V1_X + TUBE, FRONT_Y, BOTTOM_BRACE_Z,
                   CROSS_BRACE_LEN, TUBE, TUBE)
        create_box(frameComp, "Brace_Bot_Back", V1_X + TUBE, BACK_Y, BOTTOM_BRACE_Z,
                   CROSS_BRACE_LEN, TUBE, TUBE)
        
        # Mid braces at 34" (front and back) - between verticals
        create_box(frameComp, "Brace_Mid_Front", V1_X + TUBE, FRONT_Y, MID_BRACE_Z,
                   CROSS_BRACE_LEN, TUBE, TUBE)
        create_box(frameComp, "Brace_Mid_Back", V1_X + TUBE, BACK_Y, MID_BRACE_Z,
                   CROSS_BRACE_LEN, TUBE, TUBE)
        
        # TOP braces - sit ON TOP of verticals (full width, caps the vertical ends)
        create_box(frameComp, "Brace_Top_Front", V1_X, FRONT_Y, VERTICAL_HEIGHT,
                   TOTAL_WIDTH, TUBE, TUBE)
        create_box(frameComp, "Brace_Top_Back", V1_X, BACK_Y, VERTICAL_HEIGHT,
                   TOTAL_WIDTH, TUBE, TUBE)
        
        # ============================================
        # STRETCHERS - LEFT COLUMN (side-mount slides)
        # Run front-to-back, 2 per level
        # ============================================
        
        for i, h in enumerate(LEFT_HEIGHTS):
            # Left stretcher (inside of V1)
            create_box(frameComp, f"Str_Left_L_{i+1}",
                       V1_X + TUBE, FRONT_Y + TUBE, h,
                       TUBE, STRETCHER_LEN, TUBE)
            # Right stretcher (inside of V2)
            create_box(frameComp, f"Str_Left_R_{i+1}",
                       V2_X - TUBE, FRONT_Y + TUBE, h,
                       TUBE, STRETCHER_LEN, TUBE)
        
        # ============================================
        # STRETCHERS - UPPER RIGHT (side-mount slides)
        # Run front-to-back, 2 per level
        # ============================================
        
        for i, h in enumerate(UPPER_HEIGHTS):
            # Left stretcher (inside of V2)
            create_box(frameComp, f"Str_Upper_L_{i+1}",
                       V2_X + TUBE, FRONT_Y + TUBE, h,
                       TUBE, STRETCHER_LEN, TUBE)
            # Right stretcher (inside of V3)
            create_box(frameComp, f"Str_Upper_R_{i+1}",
                       V3_X - TUBE, FRONT_Y + TUBE, h,
                       TUBE, STRETCHER_LEN, TUBE)
        
        # ============================================
        # FLOOR PLATE - SPICE/ICE MAKER AREA
        # For bottom-mount slides
        # ============================================
        
        floor_plate_x = V2_X + TUBE
        floor_plate_width = RIGHT_AREA_CLEAR - TUBE
        floor_plate_z = inch(0.5)
        
        create_box(frameComp, "Floor_Plate_SpiceIce",
                   floor_plate_x, FRONT_Y + TUBE, floor_plate_z,
                   floor_plate_width, STRETCHER_LEN, TUBE)
        
        # ============================================
        # SAMPLE SHELVES (to show fit)
        # ============================================
        
        SHELF_THICK = inch(1.5)
        shelf_depth = inch(35)  # Full depth minus buffer
        
        # Left column shelf (one example)
        left_shelf_width = LEFT_COL_CLEAR - inch(0.5)
        create_box(shelfComp, "Shelf_Left_Example",
                   V1_X + TUBE + inch(0.25), FRONT_Y + inch(0.5), LEFT_HEIGHTS[0] + TUBE + inch(0.5),
                   left_shelf_width, shelf_depth, SHELF_THICK)
        
        # Upper right shelf (one example)
        upper_shelf_width = RIGHT_AREA_CLEAR - inch(1)
        create_box(shelfComp, "Shelf_Upper_Example",
                   V2_X + TUBE + inch(0.5), FRONT_Y + inch(0.5), UPPER_HEIGHTS[0] + TUBE + inch(0.5),
                   upper_shelf_width, shelf_depth, SHELF_THICK)
        
        # ============================================
        # SPICE TOWER (placeholder)
        # ============================================
        
        spice_x = V2_X + TUBE + inch(0.5)
        spice_z = floor_plate_z + TUBE + inch(0.5)
        spice_width = SPICE_CLEAR - inch(1)
        spice_height = MID_BRACE_Z - spice_z - inch(1)
        
        create_box(spiceComp, "Spice_Tower",
                   spice_x, FRONT_Y + TUBE, spice_z,
                   spice_width, shelf_depth, spice_height)
        
        # ============================================
        # ICE MAKER PLATFORM (placeholder)
        # ============================================
        
        ice_x = V2_X + TUBE + SPICE_CLEAR + inch(0.5)
        ice_z = floor_plate_z + TUBE + inch(0.5)
        ice_width = ICE_MAKER_CLEAR - inch(1)
        
        create_box(iceComp, "Ice_Maker_Platform",
                   ice_x, FRONT_Y + TUBE, ice_z,
                   ice_width, shelf_depth, inch(1.5))
        
        # ============================================
        # SUMMARY
        # ============================================
        
        summary = """Pantry Frame v5 Created!

MATERIAL: 14 gauge 1.5" square tube

DIMENSIONS:
├─ Total width: 35.5"
├─ Total depth: 36"
├─ Total height: 84" (to top of frame)
└─ Verticals: 82.5" (top brace sits on top)

WIDTH BREAKDOWN:
├─ V1: 1.5"
├─ Left column: 10" clear
├─ V2: 1.5"
├─ Right area: 21" clear (spice 5" + ice maker 15" + 1" gap)
└─ V3: 1.5"
    = 35.5" ✓

JOINT ORIENTATION (open ends hidden):
├─ Top braces sit ON TOP of verticals (caps open ends)
├─ Bottom/mid braces fit BETWEEN verticals
├─ Stretcher open ends face front/back walls
└─ All sharp edges toward walls, not user

CUT LIST:
├─ Verticals: 82.5" × 6
├─ Top cross braces: 35.5" × 2 (sit on top)
├─ Bottom/mid cross braces: 32.5" × 4
├─ Stretchers (left col): 33" × 10
├─ Stretchers (upper right): 33" × 8
└─ Floor plate: 33" × 1

SHELF HEIGHTS:
├─ Left column: 2", 16", 30", 44", 58"
└─ Upper right: 38", 50", 62", 74"

SLIDES:
├─ Side-mount: 18 (left column + upper right)
└─ Bottom-mount: 3 (spice, ice maker, RO)"""
        
        ui.messageBox(summary)
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    pass