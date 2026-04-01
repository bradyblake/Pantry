#Author: Claude (generated for Brady's pantry project)
#Description: Pantry Pull-Out Shelf Frame - COMPLETE - Fusion 360 Python Script v6
#
# COMPLETE BUILD with all components:
# - Steel frame (14 gauge 1.5" square tube)
# - All shelves (left column + upper right)
# - Slide hardware representations
# - Spice tower
# - Ice maker platform with perpendicular slide
# - RO system shelf
# - Open top shelf
#
# HOW TO USE:
# 1. Open Fusion 360
# 2. Go to Tools > Add-Ins > Scripts and Add-Ins (or press Shift+S)
# 3. Click the green "+" next to "My Scripts"
# 4. Create a new script, name it "PantryComplete"
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
        TOTAL_HEIGHT = inch(84)      # Top of frame
        
        # Steel tube (14 gauge)
        TUBE = inch(1.5)
        
        # Vertical height (top brace sits on top)
        VERTICAL_HEIGHT = inch(82.5)  # 84" - 1.5"
        
        # Width breakdown
        LEFT_COL_CLEAR = inch(10)
        SPICE_CLEAR = inch(5)
        ICE_MAKER_CLEAR = inch(15)
        RIGHT_AREA_CLEAR = inch(21)
        
        # Vertical X positions
        V1_X = 0
        V2_X = TUBE + LEFT_COL_CLEAR                # 11.5"
        V3_X = TOTAL_WIDTH - TUBE                   # 34"
        
        # Depth positions
        FRONT_Y = 0
        BACK_Y = TOTAL_DEPTH - TUBE
        
        # Lengths
        STRETCHER_LEN = TOTAL_DEPTH - (2 * TUBE)   # 33"
        CROSS_BRACE_LEN = V3_X - V1_X - TUBE       # 32.5"
        
        # Heights
        LEFT_HEIGHTS = [inch(2), inch(16), inch(30), inch(44), inch(58)]
        ICE_MAKER_TOP = inch(34)
        UPPER_HEIGHTS = [inch(38), inch(50), inch(62), inch(74)]
        
        # Shelf dimensions
        SHELF_THICK = inch(1.5)
        SHELF_DEPTH = inch(35)
        
        # Slide dimensions (representation)
        SLIDE_HEIGHT = inch(2)
        SLIDE_DEPTH = inch(24)
        SLIDE_THICK = inch(0.5)
        
        # ============================================
        # HELPER FUNCTION
        # ============================================
        
        def create_box(comp, name, x, y, z, width, depth, height):
            """Create a solid box at position (x,y,z)"""
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
        
        # Steel Frame
        frameOcc = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        frameComp = frameOcc.component
        frameComp.name = "Steel_Frame"
        
        # Slides
        slidesOcc = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        slidesComp = slidesOcc.component
        slidesComp.name = "Slides"
        
        # Left Column Shelves
        leftShelvesOcc = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        leftShelvesComp = leftShelvesOcc.component
        leftShelvesComp.name = "Left_Column_Shelves"
        
        # Upper Right Shelves
        upperShelvesOcc = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        upperShelvesComp = upperShelvesOcc.component
        upperShelvesComp.name = "Upper_Right_Shelves"
        
        # Spice Tower
        spiceOcc = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        spiceComp = spiceOcc.component
        spiceComp.name = "Spice_Tower"
        
        # Ice Maker
        iceOcc = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        iceComp = iceOcc.component
        iceComp.name = "Ice_Maker_Assembly"
        
        # RO System
        roOcc = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        roComp = roOcc.component
        roComp.name = "RO_System"
        
        # Open Top Shelf
        topShelfOcc = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        topShelfComp = topShelfOcc.component
        topShelfComp.name = "Open_Top_Shelf"
        
        # ============================================
        # STEEL FRAME - VERTICALS (6 total)
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
        # STEEL FRAME - CROSS BRACES
        # ============================================
        
        # Bottom braces (between verticals)
        create_box(frameComp, "Brace_Bot_Front", V1_X + TUBE, FRONT_Y, 0,
                   CROSS_BRACE_LEN, TUBE, TUBE)
        create_box(frameComp, "Brace_Bot_Back", V1_X + TUBE, BACK_Y, 0,
                   CROSS_BRACE_LEN, TUBE, TUBE)
        
        # Mid braces at 34" (between verticals)
        create_box(frameComp, "Brace_Mid_Front", V1_X + TUBE, FRONT_Y, ICE_MAKER_TOP,
                   CROSS_BRACE_LEN, TUBE, TUBE)
        create_box(frameComp, "Brace_Mid_Back", V1_X + TUBE, BACK_Y, ICE_MAKER_TOP,
                   CROSS_BRACE_LEN, TUBE, TUBE)
        
        # Top braces (sit ON TOP of verticals - full width)
        create_box(frameComp, "Brace_Top_Front", V1_X, FRONT_Y, VERTICAL_HEIGHT,
                   TOTAL_WIDTH, TUBE, TUBE)
        create_box(frameComp, "Brace_Top_Back", V1_X, BACK_Y, VERTICAL_HEIGHT,
                   TOTAL_WIDTH, TUBE, TUBE)
        
        # ============================================
        # STEEL FRAME - STRETCHERS (LEFT COLUMN)
        # 5 levels × 2 per level = 10 stretchers
        # Stretchers INSIDE verticals (flush with inner face)
        # ============================================
        
        for i, h in enumerate(LEFT_HEIGHTS):
            # Left stretcher (inside V1, flush with inner face)
            create_box(frameComp, f"Str_LeftCol_L_{i+1}",
                       V1_X + TUBE, FRONT_Y + TUBE, h,
                       TUBE, STRETCHER_LEN, TUBE)
            # Right stretcher (inside V2, flush with inner face)
            create_box(frameComp, f"Str_LeftCol_R_{i+1}",
                       V2_X - TUBE - TUBE, FRONT_Y + TUBE, h,
                       TUBE, STRETCHER_LEN, TUBE)
        
        # ============================================
        # STEEL FRAME - STRETCHERS (UPPER RIGHT)
        # 4 levels × 2 per level = 8 stretchers
        # Stretchers INSIDE verticals (flush with inner face)
        # ============================================
        
        for i, h in enumerate(UPPER_HEIGHTS):
            # Left stretcher (inside V2, flush with inner face)
            create_box(frameComp, f"Str_UpperRight_L_{i+1}",
                       V2_X + TUBE, FRONT_Y + TUBE, h,
                       TUBE, STRETCHER_LEN, TUBE)
            # Right stretcher (inside V3, flush with inner face)
            create_box(frameComp, f"Str_UpperRight_R_{i+1}",
                       V3_X - TUBE - TUBE, FRONT_Y + TUBE, h,
                       TUBE, STRETCHER_LEN, TUBE)
        
        # ============================================
        # STEEL FRAME - FLOOR PLATE (for bottom-mount slides)
        # ============================================
        
        floor_plate_x = V2_X + TUBE
        floor_plate_z = inch(0.5)
        
        create_box(frameComp, "Floor_Plate",
                   floor_plate_x, FRONT_Y + TUBE, floor_plate_z,
                   RIGHT_AREA_CLEAR - TUBE, STRETCHER_LEN, TUBE)
        
        # ============================================
        # SLIDES - LEFT COLUMN (side-mount, 10 total)
        # Slides mount on TOP of stretchers, facing inward
        # ============================================
        
        left_shelf_width = LEFT_COL_CLEAR - inch(0.5)
        
        for i, h in enumerate(LEFT_HEIGHTS):
            # Slide sits on top of stretcher
            slide_z = h + TUBE  # Top of stretcher
            
            # Left slide (on top of left stretcher, facing right)
            create_box(slidesComp, f"Slide_LeftCol_L_{i+1}",
                       V1_X + TUBE, FRONT_Y + TUBE, slide_z,
                       SLIDE_THICK, SLIDE_DEPTH, SLIDE_HEIGHT)
            
            # Right slide (on top of right stretcher, facing left)
            create_box(slidesComp, f"Slide_LeftCol_R_{i+1}",
                       V2_X - TUBE - TUBE, FRONT_Y + TUBE, slide_z,
                       SLIDE_THICK, SLIDE_DEPTH, SLIDE_HEIGHT)
        
        # ============================================
        # SLIDES - UPPER RIGHT (side-mount, 8 total)
        # Slides mount on TOP of stretchers
        # ============================================
        
        for i, h in enumerate(UPPER_HEIGHTS):
            slide_z = h + TUBE  # Top of stretcher
            
            # Left slide (on top of left stretcher)
            create_box(slidesComp, f"Slide_UpperRight_L_{i+1}",
                       V2_X + TUBE, FRONT_Y + TUBE, slide_z,
                       SLIDE_THICK, SLIDE_DEPTH, SLIDE_HEIGHT)
            
            # Right slide (on top of right stretcher)
            create_box(slidesComp, f"Slide_UpperRight_R_{i+1}",
                       V3_X - TUBE - TUBE, FRONT_Y + TUBE, slide_z,
                       SLIDE_THICK, SLIDE_DEPTH, SLIDE_HEIGHT)
        
        # ============================================
        # SLIDES - BOTTOM-MOUNT (spice, ice maker, RO)
        # ============================================
        
        # Spice tower bottom-mount slide (center)
        spice_slide_x = V2_X + TUBE + (SPICE_CLEAR / 2) - inch(0.5)
        create_box(slidesComp, "Slide_Spice_Bottom",
                   spice_slide_x, FRONT_Y + TUBE, floor_plate_z + TUBE,
                   inch(1), SLIDE_DEPTH, inch(0.5))
        
        # Ice maker bottom-mount slide (center)
        ice_slide_x = V2_X + TUBE + SPICE_CLEAR + (ICE_MAKER_CLEAR / 2) - inch(0.5)
        create_box(slidesComp, "Slide_Ice_Bottom",
                   ice_slide_x, FRONT_Y + TUBE, floor_plate_z + TUBE,
                   inch(1.5), SLIDE_DEPTH, inch(0.5))
        
        # ============================================
        # LEFT COLUMN SHELVES (5 shelves)
        # Shelves sit on TOP of slides
        # ============================================
        
        for i, h in enumerate(LEFT_HEIGHTS):
            # Shelf sits on top of slide: stretcher + slide height
            shelf_z = h + TUBE + SLIDE_HEIGHT
            shelf_x = V1_X + TUBE + inch(0.25)
            
            create_box(leftShelvesComp, f"Shelf_Left_{i+1}",
                       shelf_x, FRONT_Y + inch(0.5), shelf_z,
                       left_shelf_width, SHELF_DEPTH, SHELF_THICK)
        
        # ============================================
        # UPPER RIGHT SHELVES (4 shelves with spines)
        # Each shelf: two 9.75" boards + 1.5" spine = 21"
        # Shelves sit on TOP of slides
        # ============================================
        
        upper_board_width = inch(9.75)
        spine_width = TUBE
        
        for i, h in enumerate(UPPER_HEIGHTS):
            # Shelf sits on top of slide
            shelf_z = h + TUBE + SLIDE_HEIGHT
            shelf_x = V2_X + TUBE + inch(0.5)
            
            # Left board
            create_box(upperShelvesComp, f"Shelf_Upper_{i+1}_Left",
                       shelf_x, FRONT_Y + inch(0.5), shelf_z,
                       upper_board_width, SHELF_DEPTH, SHELF_THICK)
            
            # Spine (steel tube integrated)
            spine_x = shelf_x + upper_board_width
            create_box(upperShelvesComp, f"Shelf_Upper_{i+1}_Spine",
                       spine_x, FRONT_Y + inch(0.5), shelf_z,
                       spine_width, SHELF_DEPTH, SHELF_THICK)
            
            # Right board
            create_box(upperShelvesComp, f"Shelf_Upper_{i+1}_Right",
                       spine_x + spine_width, FRONT_Y + inch(0.5), shelf_z,
                       upper_board_width, SHELF_DEPTH, SHELF_THICK)
        
        # ============================================
        # SPICE TOWER
        # 5" wide × 35" deep × ~31" tall
        # ============================================
        
        spice_x = V2_X + TUBE + inch(0.5)
        spice_y = FRONT_Y + inch(0.5)
        spice_z = floor_plate_z + TUBE + inch(1)
        spice_width = SPICE_CLEAR - inch(1)
        spice_depth = SHELF_DEPTH
        spice_height = ICE_MAKER_TOP - spice_z - inch(1)
        
        # Spice tower outer box
        create_box(spiceComp, "Spice_Tower_Box",
                   spice_x, spice_y, spice_z,
                   spice_width, spice_depth, spice_height)
        
        # Internal shelves (5 levels)
        spice_shelf_spacing = spice_height / 6
        for i in range(5):
            internal_z = spice_z + spice_shelf_spacing * (i + 1)
            create_box(spiceComp, f"Spice_Internal_{i+1}",
                       spice_x + inch(0.25), spice_y + inch(0.5), internal_z,
                       spice_width - inch(0.5), spice_depth - inch(1), inch(0.5))
        
        # ============================================
        # ICE MAKER ASSEMBLY
        # Platform + ice maker + perpendicular slide
        # ============================================
        
        ice_x = V2_X + TUBE + SPICE_CLEAR + inch(0.5)
        ice_y = FRONT_Y + inch(0.5)
        ice_z = floor_plate_z + TUBE + inch(1)
        ice_platform_width = ICE_MAKER_CLEAR - inch(1)
        ice_platform_depth = SHELF_DEPTH
        
        # Main platform (slides front-to-back)
        create_box(iceComp, "Ice_Platform",
                   ice_x, ice_y, ice_z,
                   ice_platform_width, ice_platform_depth, inch(1))
        
        # Perpendicular slide rails on platform (ice maker slides left-right)
        rail_z = ice_z + inch(1)
        create_box(iceComp, "Ice_Rail_Front",
                   ice_x, ice_y + inch(2), rail_z,
                   ice_platform_width, inch(0.5), inch(0.5))
        create_box(iceComp, "Ice_Rail_Back",
                   ice_x, ice_y + ice_platform_depth - inch(4), rail_z,
                   ice_platform_width, inch(0.5), inch(0.5))
        
        # Ice maker unit (sits on rails)
        ice_maker_z = rail_z + inch(0.75)
        create_box(iceComp, "Ice_Maker_Unit",
                   ice_x + inch(1), ice_y + inch(3), ice_maker_z,
                   inch(12), inch(20), inch(15))
        
        # ============================================
        # RO SYSTEM (behind ice maker, elevated, slides forward)
        # ============================================
        
        ro_x = ice_x
        ro_y = ice_y + ice_platform_depth - inch(12)  # At back
        ro_z = ice_z + inch(3)  # Elevated above ice maker platform
        ro_width = ice_platform_width
        ro_depth = inch(10)
        
        # RO shelf
        create_box(roComp, "RO_Shelf",
                   ro_x, ro_y, ro_z,
                   ro_width, ro_depth, inch(0.75))
        
        # RO system unit
        create_box(roComp, "RO_Unit",
                   ro_x + inch(1), ro_y + inch(1), ro_z + inch(0.75),
                   ro_width - inch(2), ro_depth - inch(2), inch(12))
        
        # RO slide (front-to-back)
        create_box(roComp, "RO_Slide",
                   ro_x + ro_width/2 - inch(0.5), ro_y - inch(2), ro_z - inch(0.5),
                   inch(1), inch(14), inch(0.5))
        
        # ============================================
        # OPEN TOP SHELF (fixed, sits on top braces)
        # ============================================
        
        top_shelf_z = VERTICAL_HEIGHT + TUBE + inch(0.25)
        top_shelf_x = V1_X + TUBE + inch(0.25)
        top_shelf_width = TOTAL_WIDTH - (2 * TUBE) - inch(0.5)
        
        create_box(topShelfComp, "Open_Top_Shelf",
                   top_shelf_x, FRONT_Y + inch(0.5), top_shelf_z,
                   top_shelf_width, SHELF_DEPTH, SHELF_THICK)
        
        # ============================================
        # SUMMARY
        # ============================================
        
        summary = """COMPLETE Pantry System Created!

═══════════════════════════════════════════
STEEL FRAME (14ga 1.5" square tube)
═══════════════════════════════════════════
Verticals: 6 × 82.5"
Top cross braces: 2 × 35.5" (sit ON TOP)
Bottom/mid braces: 4 × 32.5"
Left col stretchers: 10 × 33"
Upper right stretchers: 8 × 33"
Floor plate: 1 × 33"

═══════════════════════════════════════════
SLIDES
═══════════════════════════════════════════
Side-mount (left column): 10
Side-mount (upper right): 8
Bottom-mount (spice): 1
Bottom-mount (ice maker): 1
Bottom-mount (RO): 1
TOTAL: 21 slides

═══════════════════════════════════════════
SHELVES
═══════════════════════════════════════════
Left column: 5 × (9.5" × 35")
Upper right: 4 × (21" × 35") with spines
Open top: 1 × (32.5" × 35")
TOTAL: 10 shelves

═══════════════════════════════════════════
SPECIAL COMPONENTS
═══════════════════════════════════════════
Spice tower: 4" × 35" × 31"
  - 5 internal shelves
  - Bottom-mount slide

Ice maker platform: 14" × 35"
  - Perpendicular rails for sideways slide
  - Main platform slides front-to-back

RO system: 14" × 10"
  - Elevated 3" above ice platform
  - Slides forward independently

═══════════════════════════════════════════
DIMENSIONS
═══════════════════════════════════════════
Total: 35.5"W × 36"D × 84"H

Left column: 10" clear
Right area: 21" clear
  - Spice: 5"
  - Ice maker: 15"
  - Gap: 1"

Shelf heights (left): 2", 16", 30", 44", 58"
Shelf heights (upper): 38", 50", 62", 74"
"""
        
        ui.messageBox(summary)
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    pass