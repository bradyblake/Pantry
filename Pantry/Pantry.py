#Author: Claude (generated for Brady's pantry project)
#Description: Pantry Pull-Out Shelf Frame - Fusion 360 Python Script v4
#
# FINAL CORRECTED VERSION
# - Bottom-mount slides for spice tower and ice maker (no middle vertical)
# - Side-mount slides for all other shelves
# - Proper tube thickness accounting
# - RO system shelf behind ice maker
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
        TOTAL_HEIGHT = inch(93)
        
        # Steel tube
        TUBE = inch(1.5)
        
        # Lumber
        SHELF_THICK = inch(1.5)
        
        # ============================================
        # WIDTH BREAKDOWN (35.5" total)
        # ============================================
        # | V1 | LEFT COLUMN | V2 | SPICE + ICE MAKER | V3 |
        # | 1.5|     10      |1.5 |        21         |1.5 | = 35.5" ✓
        #
        # Stretchers flush with inside face of verticals (don't eat into clear)
        
        LEFT_COL_CLEAR = inch(10)        # Clear opening for left shelves
        SPICE_CLEAR = inch(5)            # Clear width for spice tower
        ICE_MAKER_CLEAR = inch(15)       # Clear width for ice maker (actual 15", 1" extra clearance)
        RIGHT_AREA_CLEAR = inch(21)      # Combined spice + ice maker (no middle post)
        
        # Verify: 1.5 + 10 + 1.5 + 21 + 1.5 = 35.5" ✓
        # Right area: 5" spice + 15" ice maker + 1" clearance = 21"
        
        # ============================================
        # VERTICAL POSITIONS (X-axis)
        # ============================================
        
        V1_X = 0                                    # Left edge
        V2_X = TUBE + LEFT_COL_CLEAR                # Between left column and right area (1.5 + 10 = 11.5")
        V3_X = TOTAL_WIDTH - TUBE                   # Right edge (35.5 - 1.5 = 34")
        
        # Verify: V2_X + TUBE + RIGHT_AREA_CLEAR = V3_X
        # 11.5 + 1.5 + 21 = 34" = V3_X ✓
        
        # Depth positions
        FRONT_Y = 0
        BACK_Y = TOTAL_DEPTH - TUBE
        
        # Stretcher length (front to back, between posts)
        STRETCHER_LEN = TOTAL_DEPTH - (2 * TUBE)
        
        # ============================================
        # HEIGHT LEVELS
        # ============================================
        
        # Left column: 5 shelf levels spread from bottom to open shelf (0" to 84")
        # 84" / 6 spaces = ~14" between shelves
        LEFT_HEIGHTS = [inch(2), inch(16), inch(30), inch(44), inch(58)]
        
        # Upper right (above ice maker): 4 shelf levels
        # From 36" to 82" = 46" of space, 4 shelves = ~11.5" spacing
        ICE_MAKER_HEIGHT = inch(34)
        UPPER_HEIGHTS = [inch(38), inch(50), inch(62), inch(74)]
        
        # Open shelf at top (verticals end here)
        OPEN_SHELF_Z = inch(84)
        
        # RO system shelf (behind ice maker, elevated 2")
        RO_SHELF_DEPTH = inch(12)  # Shallower, sits at back
        
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
        
        roOcc = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        roComp = roOcc.component
        roComp.name = "RO_System"
        
        # ============================================
        # VERTICALS (6 total: 3 positions × front/back)
        # End at open shelf level (84") - not full height
        # ============================================
        
        VERTICAL_HEIGHT = OPEN_SHELF_Z  # 84" - verticals end at open shelf level
        
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
        # STRETCHERS - LEFT COLUMN (side-mount slides)
        # Run front-to-back, 2 per level
        # ============================================
        
        for h in LEFT_HEIGHTS:
            # Left stretcher (inside of V1)
            create_box(frameComp, f"Str_Left_L_{int(h/2.54)}",
                       V1_X + TUBE, FRONT_Y + TUBE, h,
                       TUBE, STRETCHER_LEN, TUBE)
            # Right stretcher (inside of V2)
            create_box(frameComp, f"Str_Left_R_{int(h/2.54)}",
                       V2_X - TUBE, FRONT_Y + TUBE, h,
                       TUBE, STRETCHER_LEN, TUBE)
        
        # ============================================
        # STRETCHERS - UPPER RIGHT (side-mount slides)
        # Run front-to-back, 2 per level
        # ============================================
        
        for h in UPPER_HEIGHTS:
            # Left stretcher (inside of V2)
            create_box(frameComp, f"Str_Upper_L_{int(h/2.54)}",
                       V2_X + TUBE, FRONT_Y + TUBE, h,
                       TUBE, STRETCHER_LEN, TUBE)
            # Right stretcher (inside of V3)
            create_box(frameComp, f"Str_Upper_R_{int(h/2.54)}",
                       V3_X - TUBE, FRONT_Y + TUBE, h,
                       TUBE, STRETCHER_LEN, TUBE)
        
        # ============================================
        # FLOOR PLATE - SPICE/ICE MAKER AREA (bottom-mount slides)
        # Horizontal surface for bottom-mount slide tracks
        # ============================================
        
        floor_plate_x = V2_X + TUBE
        floor_plate_width = RIGHT_AREA_CLEAR - TUBE  # Clear area minus some margin
        floor_plate_z = inch(0.5)  # Slightly off ground
        
        create_box(frameComp, "Floor_Plate_SpiceIce",
                   floor_plate_x, FRONT_Y + TUBE, floor_plate_z,
                   floor_plate_width, STRETCHER_LEN, TUBE)
        
        # ============================================
        # CROSS BRACES
        # ============================================
        
        # Bottom - full width
        create_box(frameComp, "Brace_Bot_Front", 0, FRONT_Y, 0, TOTAL_WIDTH, TUBE, TUBE)
        create_box(frameComp, "Brace_Bot_Back", 0, BACK_Y, 0, TOTAL_WIDTH, TUBE, TUBE)
        
        # At ice maker top (34") - full width
        create_box(frameComp, "Brace_34_Front", 0, FRONT_Y, ICE_MAKER_HEIGHT, TOTAL_WIDTH, TUBE, TUBE)
        create_box(frameComp, "Brace_34_Back", 0, BACK_Y, ICE_MAKER_HEIGHT, TOTAL_WIDTH, TUBE, TUBE)
        
        # At open shelf level - this is the TOP of the frame now
        create_box(frameComp, "Brace_Open_Front", 0, FRONT_Y, OPEN_SHELF_Z - TUBE, TOTAL_WIDTH, TUBE, TUBE)
        create_box(frameComp, "Brace_Open_Back", 0, BACK_Y, OPEN_SHELF_Z - TUBE, TOTAL_WIDTH, TUBE, TUBE)
        
        # ============================================
        # LEFT COLUMN SHELVES (5 levels)
        # 10" clear opening, shelf slightly narrower for slide clearance
        # ============================================
        
        shelf_depth = TOTAL_DEPTH - (2 * TUBE) - inch(1)
        left_shelf_width = LEFT_COL_CLEAR - inch(0.5)  # 9.5" shelf in 10" opening
        
        for i, h in enumerate(LEFT_HEIGHTS):
            shelf_z = h + TUBE + inch(0.5)
            create_box(shelfComp, f"Shelf_Left_{i+1}",
                       V1_X + TUBE + inch(0.5), FRONT_Y + TUBE, shelf_z,
                       left_shelf_width, shelf_depth, SHELF_THICK)
        
        # ============================================
        # UPPER RIGHT SHELVES (4 levels, 21" wide with spine)
        # ============================================
        
        upper_shelf_width = RIGHT_AREA_CLEAR - inch(1)
        board_width = inch(9.5)  # Each board (two boards + spine = 21")
        
        for i, h in enumerate(UPPER_HEIGHTS):
            shelf_z = h + TUBE + inch(0.5)
            shelf_x = V2_X + TUBE + inch(0.5)
            
            # Left board
            create_box(shelfComp, f"Shelf_Upper_{i+1}_L",
                       shelf_x, FRONT_Y + TUBE, shelf_z,
                       board_width, shelf_depth, SHELF_THICK)
            
            # Spine (integrated, same height as boards)
            spine_x = shelf_x + board_width
            create_box(shelfComp, f"Spine_Upper_{i+1}",
                       spine_x, FRONT_Y + TUBE, shelf_z,
                       TUBE, shelf_depth, SHELF_THICK)
            
            # Right board
            create_box(shelfComp, f"Shelf_Upper_{i+1}_R",
                       spine_x + TUBE, FRONT_Y + TUBE, shelf_z,
                       board_width, shelf_depth, SHELF_THICK)
        
        # ============================================
        # SPICE TOWER (bottom-mount slide, no middle support)
        # ============================================
        
        spice_x = V2_X + TUBE + inch(0.5)
        spice_z = floor_plate_z + TUBE + inch(0.5)  # Sits above floor plate
        spice_width = SPICE_CLEAR - inch(1)
        spice_height = ICE_MAKER_HEIGHT - spice_z - inch(1)
        
        create_box(spiceComp, "Spice_Tower",
                   spice_x, FRONT_Y + TUBE, spice_z,
                   spice_width, shelf_depth, spice_height)
        
        # Spice bottom-mount slide track (centered under spice tower)
        slide_track_x = spice_x + (spice_width / 2) - (TUBE / 2)
        create_box(spiceComp, "Spice_Slide_Track",
                   slide_track_x, FRONT_Y + TUBE, floor_plate_z,
                   TUBE, STRETCHER_LEN, inch(0.5))
        
        # ============================================
        # ICE MAKER PLATFORM (bottom-mount slide)
        # ============================================
        
        ice_x = V2_X + TUBE + SPICE_CLEAR + inch(0.5)
        ice_z = floor_plate_z + TUBE + inch(0.5)
        ice_width = ICE_MAKER_CLEAR - inch(1)
        ice_platform_height = inch(1.5)  # Platform thickness
        
        # Platform that ice maker sits on
        create_box(iceComp, "Ice_Maker_Platform",
                   ice_x, FRONT_Y + TUBE, ice_z,
                   ice_width, shelf_depth, ice_platform_height)
        
        # Ice maker box (representation)
        create_box(iceComp, "Ice_Maker_Box",
                   ice_x + inch(0.5), FRONT_Y + TUBE + inch(0.5), ice_z + ice_platform_height,
                   ice_width - inch(1), inch(24), inch(30))
        
        # Ice maker bottom-mount slide track (centered)
        ice_slide_x = ice_x + (ice_width / 2) - (TUBE / 2)
        create_box(iceComp, "Ice_Slide_Track",
                   ice_slide_x, FRONT_Y + TUBE, floor_plate_z,
                   TUBE, STRETCHER_LEN, inch(0.5))
        
        # ============================================
        # RO SYSTEM SHELF (behind ice maker, elevated 2", slides forward)
        # ============================================
        
        ro_x = ice_x
        ro_y = BACK_Y - RO_SHELF_DEPTH  # At back of cubby
        ro_z = ice_z + inch(2)  # Elevated 2" above ice maker platform level
        ro_width = ice_width
        
        create_box(roComp, "RO_Shelf",
                   ro_x, ro_y, ro_z,
                   ro_width, RO_SHELF_DEPTH, SHELF_THICK)
        
        # RO system box (representation)
        create_box(roComp, "RO_System_Box",
                   ro_x + inch(1), ro_y + inch(1), ro_z + SHELF_THICK,
                   ro_width - inch(2), RO_SHELF_DEPTH - inch(2), inch(18))
        
        # ============================================
        # OPEN TOP SHELF (fixed, full width)
        # ============================================
        
        create_box(shelfComp, "Open_Shelf_Top",
                   V1_X + TUBE + inch(0.25), FRONT_Y + TUBE, OPEN_SHELF_Z + TUBE,
                   TOTAL_WIDTH - (2 * TUBE) - inch(0.5), shelf_depth, SHELF_THICK)
        
        # ============================================
        # SUMMARY
        # ============================================
        
        summary = """Pantry Frame v4 Created!

DIMENSIONS (35.5" total width):
├─ V1: 1.5"
├─ Left column: 10" clear
├─ V2: 1.5"  
├─ Right area: 21" clear (spice 5" + ice maker 15" + 1" clearance)
└─ V3: 1.5"
    = 35.5" ✓

LAYOUT:
┌──────────────────────────────────────┐ 93" (ceiling)
│         (open to ceiling)            │
├──────────┬───────────────────────────┤ 84" (verticals end here)
│   OPEN SHELF (fixed, full width)     │
├──────────┼───────────────────────────┤ 74"
│   10"    │        21" shelf          │
├──────────┼───────────────────────────┤ 62"
│   10"    │        21" shelf          │
├──────────┼───────────────────────────┤ 50"
│   10"    │        21" shelf          │
├──────────┼───────────────────────────┤ 38"
│   10"    │        21" shelf          │
├──────────┼─────┬────────────────────┤ 34"
│   10"    │ 5"  │   ICE MAKER 15"    │
│          │SPICE│    + RO behind     │
└──────────┴─────┴────────────────────┘

LEFT COLUMN SHELF HEIGHTS: 2", 16", 30", 44", 58"
UPPER RIGHT SHELF HEIGHTS: 38", 50", 62", 74"

SLIDES:
- Left column: 10 side-mount (5 levels × 2)
- Upper right: 8 side-mount (4 levels × 2)
- Spice tower: 1 bottom-mount center
- Ice maker: 1 bottom-mount center (heavy duty)

VERTICALS END AT 84" (open shelf level)"""
        
        ui.messageBox(summary)
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    pass