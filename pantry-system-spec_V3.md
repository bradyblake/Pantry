# PantryPal: Smart Pantry Inventory System

## Project Overview

PantryPal is a touchscreen-based pantry inventory management system that combines passive sensor monitoring with manual input to track household food inventory. The system integrates with a recipe database to provide meal recommendations based on available ingredients.

### Core Philosophy
- **Minimal user friction**: The system should work with lazy humans (especially kids)
- **Passive where possible**: Cameras and weight sensors do the heavy lifting
- **Smart prompting**: When user input is needed, make it dead simple
- **Meal-planning focused**: The real value is "what can I cook tonight?"

---

## System Architecture

### Hardware Components

```
┌────────────────────────────────────────────────────────────────┐
│                    RASPBERRY PI 4 (4GB+)                       │
│                      Central Controller                         │
└──────────────────────────┬─────────────────────────────────────┘
                           │
       ┌───────────────────┼───────────────────┬─────────────────┐
       │                   │                   │                 │
       ▼                   ▼                   ▼                 ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐   ┌───────────┐
│ Touchscreen │    │   Weight    │    │   Pouch     │   │  Receipt  │
│  Display    │    │  Sensors    │    │   Camera    │   │  Camera   │
│  10" HDMI   │    │  (ESP32 +   │    │  (Pi Cam)   │   │ (Pi Cam   │
│             │    │   HX711)    │    │             │   │  or Phone)│
└─────────────┘    └─────────────┘    └─────────────┘   └───────────┘
```

### Software Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Frontend | Svelte + Tailwind CSS | Lightweight, reactive, touch-friendly |
| Backend API | Python + FastAPI | Hardware integration, extensive libraries |
| Database | SQLite | Simple, embedded, sufficient for scale |
| Vision/OCR | Claude API | Receipt parsing, product recognition |
| Barcode Reading | pyzbar + OpenCV | Fast local barcode decoding |
| Hardware Comm | Python GPIO, pyserial | Direct sensor communication |
| Process Manager | systemd | Auto-start, crash recovery |

### Display: iPad 4th Generation

The primary display is a repurposed iPad 4th Generation (MD513LL/A):
- 9.7" Retina display, 2048×1536 resolution
- iOS 10.3.3 (max supported version)
- 1GB RAM
- Accesses PantryPal via Safari or native WebView wrapper

```
┌─────────────────┐         WiFi         ┌─────────────────┐
│  Raspberry Pi   │◄───────────────────►│      iPad       │
│                 │                      │                 │
│  • Backend API  │    HTTP/WebSocket    │  • Safari or    │
│  • Database     │◄───────────────────►│    WebView app  │
│  • Voice I/O    │                      │  • Touch UI     │
│  • Hardware     │                      │  • Display only │
└─────────────────┘                      └─────────────────┘
        │
        │ USB
        ▼
┌─────────────────┐
│ USB Speakerphone│
│ (voice I/O)     │
└─────────────────┘
```

### iOS 10 Safari Compatibility

The frontend must work within iOS 10 Safari's limitations:

**Use these (well-supported):**
- Vanilla JavaScript or Svelte (compiles to clean ES5/ES6)
- Flexbox for layout
- CSS transitions and transforms
- Fetch API
- WebSocket (for real-time updates)
- LocalStorage

**Avoid these (broken or missing):**
- CSS Grid (partial support, buggy)
- Modern JS syntax (optional chaining `?.`, nullish coalescing `??`)
- Heavy frameworks (React, Vue runtime overhead)
- Service Workers
- Web Audio API / getUserMedia (mic access broken)

**Vite config for iOS 10 compatibility:**
```javascript
// vite.config.js
export default {
  build: {
    target: 'es2015',
  }
}
```

### WebView Wrapper App (Plan B)

If Safari limitations become problematic, a minimal native iOS app wraps the web UI:

```objectivec
// ViewController.m - Full-screen WebView pointing to Pi
- (void)viewDidLoad {
    [super viewDidLoad];
    
    WKWebViewConfiguration *config = [[WKWebViewConfiguration alloc] init];
    self.webView = [[WKWebView alloc] initWithFrame:self.view.bounds configuration:config];
    [self.view addSubview:self.webView];
    
    NSURL *url = [NSURL URLWithString:@"http://RASPBERRY_PI_IP:8000"];
    [self.webView loadRequest:[NSURLRequest requestWithURL:url]];
}
```

**Benefits:**
- Full-screen (no Safari chrome)
- Feels like a dedicated app
- Same web codebase
- Guided Access works for kiosk mode

**Requirements:**
- Mac with Xcode 12
- Free Apple ID (7-day cert) or $99/yr dev account (1-year cert)

### Voice Architecture

Since iOS 10 Safari can't access the microphone reliably, voice I/O is handled entirely by the Pi:

```
┌─────────────────────────────────────────────────────────────────┐
│                      VOICE FLOW                                  │
│                                                                  │
│  1. "Hey PantryPal, find ingredients for tacos"                 │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────────┐                                            │
│  │ USB Speakerphone│ ──► Raspberry Pi                           │
│  └─────────────────┘         │                                  │
│                              ├─► Wake word detection (Porcupine)│
│                              ├─► Speech-to-text (Whisper)       │
│                              ├─► Intent parsing                  │
│                              ├─► Query inventory/recipes         │
│                              ├─► Send LED commands (MQTT)        │
│                              └─► Text-to-speech response         │
│                                        │                         │
│  2. LEDs light up ingredient locations │                         │
│                                        ▼                         │
│  3. Voice: "Found 4 ingredients..."   Speaker                   │
│                                                                  │
│  4. iPad shows visual feedback via WebSocket                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### UI Design Guidelines

Given the 1GB RAM and kitchen environment:

| Guideline | Requirement |
|-----------|-------------|
| Touch targets | 64×64px minimum for buttons |
| Font size | 18-20px for readability |
| DOM weight | Keep light — paginate long lists |
| Updates | Debounce real-time changes |
| Images | Compress, lazy load |
| Testing | Test on actual iPad, not just simulator |

---

## Database Schema

### Core Tables

```sql
-- Products: Master list of all known products
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode TEXT UNIQUE,
    name TEXT NOT NULL,
    category TEXT,
    subcategory TEXT,
    default_unit TEXT DEFAULT 'unit',  -- unit, oz, lb, g, ml, etc.
    default_quantity REAL DEFAULT 1,
    shelf_life_days INTEGER,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inventory: Current stock levels
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    quantity REAL NOT NULL DEFAULT 0,
    location TEXT,  -- 'pantry_shelf_1', 'pouch_bin', 'fridge', 'freezer'
    expiration_date DATE,
    -- Freezer-specific fields
    frozen_date DATE,
    freeze_by_date DATE,
    container_description TEXT,  -- "red lid container", "blue freezer bag, bottom drawer"
    photo_path TEXT,  -- Photo of item when frozen
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Freezer Audits: Track periodic freezer inventory checks
CREATE TABLE freezer_audits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    photo_path TEXT,
    items_confirmed INTEGER,
    items_removed INTEGER,
    notes TEXT
);

-- Inventory Log: All additions and removals
CREATE TABLE inventory_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    quantity_change REAL NOT NULL,  -- positive = add, negative = use
    source TEXT NOT NULL,  -- 'manual', 'receipt_scan', 'weight_sensor', 'pouch_camera'
    confidence REAL DEFAULT 1.0,  -- 0-1, for sensor-detected changes
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Weight Sensors: Configuration and state
CREATE TABLE weight_sensors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id TEXT UNIQUE NOT NULL,  -- hardware identifier
    location TEXT NOT NULL,
    description TEXT,
    calibration_offset REAL DEFAULT 0,
    calibration_scale REAL DEFAULT 1,
    last_weight_grams REAL,
    last_reading_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Weight Events: Raw weight change detections
CREATE TABLE weight_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER NOT NULL,
    weight_before_grams REAL,
    weight_after_grams REAL,
    weight_delta_grams REAL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_product_id INTEGER,
    resolved_at TIMESTAMP,
    FOREIGN KEY (sensor_id) REFERENCES weight_sensors(id),
    FOREIGN KEY (resolved_product_id) REFERENCES products(id)
);

-- Recipes
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    instructions TEXT,
    prep_time_minutes INTEGER,
    cook_time_minutes INTEGER,
    servings INTEGER,
    source TEXT,  -- 'manual', 'imported', 'cookbook_scan'
    source_url TEXT,
    image_url TEXT,
    tags TEXT,  -- JSON array: ["quick", "kid-friendly", "mexican"]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recipe Ingredients: Links recipes to products
CREATE TABLE recipe_ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    product_id INTEGER,  -- NULL if ingredient not matched to inventory
    ingredient_text TEXT NOT NULL,  -- Original text, e.g., "1 lb ground beef"
    quantity REAL,
    unit TEXT,
    is_optional BOOLEAN DEFAULT FALSE,
    notes TEXT,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Shopping List
CREATE TABLE shopping_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    custom_item_name TEXT,  -- For items not in products table
    quantity REAL,
    unit TEXT,
    checked BOOLEAN DEFAULT FALSE,
    added_reason TEXT,  -- 'manual', 'recipe', 'low_stock'
    recipe_id INTEGER,  -- If added for a specific recipe
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id)
);

-- Pouch Sightings: Camera detections of pouches
CREATE TABLE pouch_sightings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    barcode TEXT,
    image_path TEXT,
    confidence REAL,
    sighting_type TEXT,  -- 'present', 'added', 'removed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- User Preferences
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes for Performance

```sql
CREATE INDEX idx_inventory_product ON inventory(product_id);
CREATE INDEX idx_inventory_log_product ON inventory_log(product_id);
CREATE INDEX idx_inventory_log_created ON inventory_log(created_at);
CREATE INDEX idx_weight_events_unresolved ON weight_events(resolved) WHERE resolved = FALSE;
CREATE INDEX idx_recipe_ingredients_recipe ON recipe_ingredients(recipe_id);
CREATE INDEX idx_recipe_ingredients_product ON recipe_ingredients(product_id);
CREATE INDEX idx_products_barcode ON products(barcode);
CREATE INDEX idx_products_category ON products(category);
```

---

## API Endpoints

### Products

```
GET    /api/products                    # List all products (with search/filter)
GET    /api/products/{id}               # Get single product
POST   /api/products                    # Create product
PUT    /api/products/{id}               # Update product
DELETE /api/products/{id}               # Delete product
GET    /api/products/barcode/{barcode}  # Lookup by barcode
POST   /api/products/lookup-barcode     # Lookup barcode via external API if unknown
```

### Inventory

```
GET    /api/inventory                   # Current inventory state
GET    /api/inventory/low-stock         # Items below threshold
POST   /api/inventory/add               # Add stock (manual or receipt)
POST   /api/inventory/use               # Use/remove stock
GET    /api/inventory/log               # View history (with filters)
GET    /api/inventory/product/{id}      # History for specific product
```

### Freezer

```
GET    /api/freezer                     # All freezer contents
GET    /api/freezer/oldest              # Items frozen longest (use soon)
GET    /api/freezer/expiring            # Items approaching freeze-by date
POST   /api/freezer/add                 # Add item to freezer
PUT    /api/freezer/{id}                # Update freezer item
DELETE /api/freezer/{id}                # Remove item (used or discarded)
POST   /api/freezer/audit/start         # Begin freezer audit
POST   /api/freezer/audit/complete      # Complete audit with confirmations
GET    /api/freezer/audit/history       # Past audit records
GET    /api/freezer/suggestions         # "Use these soon" suggestions
```

### Weight Sensors

```
GET    /api/sensors                     # List all sensors
GET    /api/sensors/{id}                # Sensor details + recent events
POST   /api/sensors/{id}/calibrate      # Set calibration values
GET    /api/sensors/events/unresolved   # Pending weight changes needing resolution
POST   /api/sensors/events/{id}/resolve # Resolve a weight event to a product
POST   /api/sensors/events/{id}/dismiss # Dismiss (ignore) a weight event
```

### Pouch Camera

```
GET    /api/pouch/status                # Camera status, recent detections
GET    /api/pouch/inventory             # Current pouch inventory based on sightings
POST   /api/pouch/snapshot              # Trigger manual scan
GET    /api/pouch/sightings             # View detection history
```

### Recipes

```
GET    /api/recipes                     # List all recipes (with search/filter)
GET    /api/recipes/{id}                # Get recipe with ingredients
POST   /api/recipes                     # Create recipe manually
PUT    /api/recipes/{id}                # Update recipe
DELETE /api/recipes/{id}                # Delete recipe
POST   /api/recipes/import-url          # Import from website URL
POST   /api/recipes/scan-photo          # Import from photo (cookbook page)
GET    /api/recipes/suggestions         # Get meal suggestions based on inventory
GET    /api/recipes/{id}/can-make       # Check if have ingredients for specific recipe
POST   /api/recipes/{id}/make           # Log that recipe was made (decrements inventory)
```

### Receipt Scanning

```
POST   /api/receipts/scan               # Upload receipt image for processing
GET    /api/receipts/{id}               # Get parsed receipt results
POST   /api/receipts/{id}/confirm       # Confirm and apply to inventory
GET    /api/receipts/history            # Past receipt scans
```

### Shopping List

```
GET    /api/shopping                    # Get current shopping list
POST   /api/shopping                    # Add item to list
PUT    /api/shopping/{id}               # Update item (quantity, checked)
DELETE /api/shopping/{id}               # Remove item
POST   /api/shopping/generate           # Auto-generate from low stock
POST   /api/shopping/from-recipe/{id}   # Add missing ingredients for recipe
DELETE /api/shopping/clear-checked      # Remove all checked items
```

### System

```
GET    /api/system/status               # System health, sensor status
GET    /api/system/settings             # Get all settings
PUT    /api/system/settings             # Update settings
POST   /api/system/backup               # Trigger database backup
```

---

## Frontend UI Specification

### Main Screen Layout

```
┌────────────────────────────────────────────────────────────────────┐
│  PantryPal                                    [⚙️]  [🔔 3]         │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                     TONIGHT'S SUGGESTIONS                     │  │
│  │                                                               │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │  │
│  │  │  Tacos  │  │ Chicken │  │  Pasta  │  │  More   │        │  │
│  │  │  🌮     │  │  & Rice │  │ Alfredo │  │   →     │        │  │
│  │  │ Ready!  │  │  🍗     │  │  🍝     │  │         │        │  │
│  │  │         │  │ Ready!  │  │ Need: 1 │  │         │        │  │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐   │
│  │                  │ │                  │ │                  │   │
│  │    INVENTORY     │ │       USE        │ │    ADD STOCK     │   │
│  │                  │ │                  │ │                  │   │
│  │    📦            │ │       ➖          │ │       ➕          │   │
│  │                  │ │                  │ │                  │   │
│  │  View all items  │ │  Log what you    │ │  Scan receipt    │   │
│  │                  │ │  used            │ │  or add items    │   │
│  │                  │ │                  │ │                  │   │
│  └──────────────────┘ └──────────────────┘ └──────────────────┘   │
│                                                                    │
│  ┌──────────────────────────────────────┐ ┌─────────────────────┐  │
│  │  🧊  FREEZER                          │ │  📋  SHOPPING      │  │
│  │  12 items • 2 use soon               │ │  LIST (8 items)    │  │
│  └──────────────────────────────────────┘ └─────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  ⚠️  Sensor Alert: Something removed from Shelf 2 at 6:32pm  │  │
│  │     [Cheerios]  [Goldfish]  [Other...]            [Dismiss]  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  🧊  Freezer: Ground beef frozen 98 days ago — use soon!     │  │
│  │     [View Freezer]  [Find Recipes Using It]       [Dismiss]  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### INVENTORY Screen

```
┌────────────────────────────────────────────────────────────────────┐
│  ← Back              INVENTORY                    [🔍 Search]      │
├────────────────────────────────────────────────────────────────────┤
│  [All] [Pantry] [Fridge] [🧊Freezer] [Pouches] [Low Stock]        │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  CEREALS & BREAKFAST                                              │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ 🟢  Cheerios                           2 boxes              │  │
│  │ 🟡  Goldfish Crackers                  1 bag (low)          │  │
│  │ 🟢  Oatmeal                            1 container          │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  CANNED GOODS                                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ 🟢  Diced Tomatoes                     4 cans               │  │
│  │ 🟢  Black Beans                        3 cans               │  │
│  │ 🔴  Chicken Broth                      0 (out!)             │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  SEASONING POUCHES                                                │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ 🟢  Taco Seasoning                     3 packets            │  │
│  │ 🟢  Brown Gravy Mix                    2 packets            │  │
│  │ 🟡  Ranch Dip Mix                      1 packet (low)       │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### USE Screen

```
┌────────────────────────────────────────────────────────────────────┐
│  ← Back                  USE                                       │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  🔍  Search or scan barcode...                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  RECENT ITEMS                                                      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐             │
│  │Cheerios │  │  Taco   │  │  Diced  │  │  Pasta  │             │
│  │         │  │Seasoning│  │ Tomato  │  │         │             │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘             │
│                                                                    │
│  ─────────────────────────────────────────────────────────────── │
│                                                                    │
│  PENDING SENSOR DETECTIONS                                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Shelf 2: -14oz detected at 6:32pm                           │  │
│  │  What was removed?                                            │  │
│  │  [Cheerios] [Goldfish] [Crackers] [Something else...]       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Pouch bin: Taco Seasoning removed at 5:45pm                 │  │
│  │  [Confirm ✓]                              [Wasn't me ✗]      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### ADD STOCK Screen

```
┌────────────────────────────────────────────────────────────────────┐
│  ← Back              ADD STOCK                                     │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                                                               │  │
│  │               📷  SCAN RECEIPT                                │  │
│  │                                                               │  │
│  │          Take a photo of your grocery receipt                 │  │
│  │                                                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                                                               │  │
│  │               🔍  SCAN BARCODE                                │  │
│  │                                                               │  │
│  │           Scan individual item barcodes                       │  │
│  │                                                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                                                               │  │
│  │               ✏️  MANUAL ENTRY                                │  │
│  │                                                               │  │
│  │           Search and add items by name                        │  │
│  │                                                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Receipt Scan Confirmation Screen

```
┌────────────────────────────────────────────────────────────────────┐
│  ← Back           CONFIRM RECEIPT                    [Rescan]      │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Walmart - January 26, 2026                                       │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ ✓  Cheerios 18oz                              1    $4.99     │  │
│  │ ✓  McCormick Taco Seasoning                   3    $3.57     │  │
│  │ ✓  Hunt's Diced Tomatoes 14oz                 2    $2.98     │  │
│  │ ✓  Great Value Black Beans                    4    $3.16     │  │
│  │                                                               │  │
│  │ ⚠️  "GV DICE TOM 28" — What is this?                         │  │
│  │    [Diced Tomatoes 28oz]  [Diced Tomatoes w/Green Chiles]    │  │
│  │    [Something else...]                                        │  │
│  │                                                               │  │
│  │ ⚠️  "BNLS CHKN BRST" — What is this?                         │  │
│  │    [Boneless Chicken Breast]  [Skip - not pantry item]       │  │
│  │    [Something else...]                                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ────────────────────────────────────────────────────────────────  │
│                                                                    │
│        ┌────────────────────────────────────────────┐             │
│        │          CONFIRM & ADD TO INVENTORY         │             │
│        └────────────────────────────────────────────┘             │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Recipe Detail Screen

```
┌────────────────────────────────────────────────────────────────────┐
│  ← Back                TACOS                         [Edit] [🗑️]  │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                        🌮                                     │  │
│  │                                                               │  │
│  │  Prep: 15 min  |  Cook: 20 min  |  Serves: 4                 │  │
│  │                                                               │  │
│  │  Tags: #quick #mexican #kid-friendly                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  INGREDIENTS                              STATUS                   │
│  ──────────────────────────────────────────────────────────────── │
│  1 lb ground beef                         ❓ Not tracked          │
│  1 packet taco seasoning                  ✅ Have 3               │
│  8 taco shells                            ❓ Not tracked          │
│  1 cup shredded cheese                    ❓ Not tracked          │
│  1 can diced tomatoes                     ✅ Have 4               │
│  Lettuce (optional)                       ⚪ Optional             │
│  Sour cream (optional)                    ⚪ Optional             │
│                                                                    │
│  ────────────────────────────────────────────────────────────────  │
│                                                                    │
│   ┌─────────────────┐        ┌─────────────────────────────┐      │
│   │   MAKE THIS     │        │  ADD MISSING TO SHOPPING    │      │
│   │  (log usage)    │        │         LIST                │      │
│   └─────────────────┘        └─────────────────────────────┘      │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Notification/Alert Banner (persistent on main screen)

```
┌────────────────────────────────────────────────────────────────────┐
│  🔔  3 items need attention                              [View]   │
│                                                                    │
│  • Weight change on Shelf 2 — what was used?                      │
│  • Chicken Broth is out of stock                                  │
│  • Goldfish Crackers running low                                  │
└────────────────────────────────────────────────────────────────────┘
```

---

## Installation During Pantry Construction

Since the pantry frame is still being built, this is the ideal time to run wiring for the tracking system. The hybrid approach uses different tracking methods optimized for each zone.

### Tracking Method by Zone

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONT VIEW                                   │
│                                                                      │
│    V1 (Ice Maker)         V2 (Middle)           V3 (Spice Tower)   │
│    ┌─────────────┐       ┌─────────────┐       ┌─────────────┐     │
│ 58"│ ┌─────────┐ │       │ ┌─────────┐ │       │             │     │
│    │ │ SHELF 3 │ │       │ │ SHELF 3 │ │       │   SPICE     │     │
│    │ │ 📷 [RGB]│ │       │ │ 📷 [RGB]│ │       │   TOWER     │     │
│    │ │ Camera  │ │       │ │ Camera  │ │       │             │     │
│    │ └─────────┘ │       │ └─────────┘ │       │  📡 RFID    │     │
│ 44"│ ┌─────────┐ │       │ ┌─────────┐ │       │  📷 Camera  │     │
│    │ │ SHELF 2 │ │       │ │ SHELF 2 │ │       │  [RGB]      │     │
│    │ │ 📷 [RGB]│ │       │ │🥫 CANS  │ │       │             │     │
│    │ │ Camera  │ │       │ │ Laser   │ │       │             │     │
│    │ └─────────┘ │       │ └─────────┘ │       ├─────────────┤     │
│ 30"│ ┌─────────┐ │       │ ┌─────────┐ │       │ ┌─────────┐ │     │
│    │ │ SHELF 1 │ │       │ │ SHELF 1 │ │       │ │Pouch Bin│ │     │
│    │ │📡 RFID  │ │       │ │ 📷 [RGB]│ │       │ │📷 Barcode│     │
│    │ │📷 Camera│ │       │ │ Camera  │ │       │ │ [RGB]   │ │     │
│    │ │ [RGB]   │ │       │ │         │ │       │ └─────────┘ │     │
│    │ └─────────┘ │       │ └─────────┘ │       │             │     │
│    │             │       │             │       │             │     │
│    │ [Ice Maker] │       │             │       │             │     │
│    └─────────────┘       └─────────────┘       └─────────────┘     │
│                                                                      │
│    LEGEND:                                                          │
│    📷 = ESP32-CAM (image recognition, fill level, packaged goods)  │
│    📡 = UHF RFID antenna (bulk containers, position tracking)       │
│    🥫 = Laser break sensor (can rotation counting)                  │
│    [RGB] = WS2812B LED strip (zone feedback)                        │
└─────────────────────────────────────────────────────────────────────┘
```

### Sensor Zone Summary

| Zone | Location | Tracking Method | Purpose |
|------|----------|-----------------|---------|
| 1 | V1 Shelf 1 (30") | **RFID + Camera + RGB** | Bulk food containers (flour, sugar, rice) |
| 2 | V1 Shelf 2 (44") | Camera + RGB | General packaged goods |
| 3 | V1 Shelf 3 (58") | Camera + RGB | General packaged goods |
| 4 | V2 Shelf 1 (30") | Camera + RGB | General packaged goods |
| 5 | V2 Shelf 2 (44") | **Laser encoder** | Can rotation system (FIFO) |
| 6 | V2 Shelf 3 (58") | Camera + RGB | General packaged goods |
| 7 | V3 Spice Tower | **RFID + Camera + RGB** | Spice containers (grab & go) |
| 8 | V3 Pouch Bin | Camera + RGB | Seasoning pouches (barcode scan) |

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SYSTEM ARCHITECTURE                          │
│                                                                      │
│                        ┌─────────────────┐                          │
│                        │  Raspberry Pi 4 │                          │
│                        │                 │                          │
│                        │  • PantryPal SW │                          │
│                        │  • Claude API   │                          │
│                        │  • Web UI       │                          │
│                        └────────┬────────┘                          │
│                                 │                                    │
│              ┌──────────────────┼──────────────────┐                │
│              │                  │                  │                │
│              ▼                  ▼                  ▼                │
│     ┌────────────────┐ ┌──────────────┐ ┌─────────────────┐        │
│     │  UHF RFID      │ │  USB Hub     │ │  Touchscreen    │        │
│     │  Reader        │ │  (Powered)   │ │  10"            │        │
│     │  (4-port)      │ │              │ │                 │        │
│     └───────┬────────┘ └──────┬───────┘ └─────────────────┘        │
│             │                 │                                      │
│    ┌────────┴────────┐        │                                      │
│    │                 │        │                                      │
│    ▼                 ▼        ▼                                      │
│ [Antenna 1]    [Antenna 2]  [ESP32-CAMs × 6]                        │
│ V1 Shelf 1     V3 Spice     (one per shelf)                         │
│ Bulk Foods     Tower         │                                      │
│                              ├── Camera (image capture)             │
│                              ├── RGB strip (zone feedback)          │
│                              └── PIR sensor (motion trigger)        │
│                                                                      │
│                           [ESP32 + Laser Sensors]                   │
│                           V2 Shelf 2 - Can Rotation                 │
│                              ├── IR break beams (×2 per lane)       │
│                              └── Counts cans IN and OUT             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Camera + RGB Feedback System

Each camera shelf has an ESP32-CAM with RGB LED strip for visual feedback.

**LED Behavior:**

| State | Color | Meaning |
|-------|-------|---------|
| Idle | Off or dim white | Monitoring |
| Change detected | 🔴 RED (zone) | Scanning that area... |
| Can't identify | 🟡 YELLOW (zone) | Check touchscreen to confirm |
| Logged successfully | 🟢 GREEN (zone) | Got it! |
| Return item here | 🔵 BLUE (pulsing) | RFID item returning, put it here |
| Add stock mode | 🔵 BLUE (solid) | Scan items IN |

**Zone-based feedback:**

```
SHELF TOP-DOWN VIEW - ZONE DETECTION
────────────────────────────────────

Camera divides shelf into zones matching LED segments:

    LED Strip: [Zone1][Zone2][Zone3][Zone4][Zone5][Zone6]
                  │      │      │      │      │      │
    Camera:    ┌──────┬──────┬──────┬──────┬──────┬──────┐
               │      │      │      │      │      │      │
               │      │  ██  │      │      │      │      │ ← Change here
               │      │      │      │      │      │      │
               └──────┴──────┴──────┴──────┴──────┴──────┘
                         ↓
               LED Zone 3 lights RED
                         ↓
               AI identifies: "Cheerios removed"
                         ↓
               LED Zone 3 lights GREEN
```

### UHF RFID System

Single 4-port reader covers both RFID zones with directional antennas.

**Coverage:**

```
UHF RFID ANTENNA PLACEMENT
──────────────────────────

V1 Shelf 1 (Bulk Foods):
┌─────────────────────────────────────┐
│  [Antenna 1 - mounted at back]      │
│         ↓  ↓  ↓  ↓  ↓               │
│  [Flour] [Sugar] [Rice] [Oats]      │
│    ⬡       ⬡      ⬡      ⬡          │  ← RFID tags on containers
└─────────────────────────────────────┘

V3 Spice Tower:
┌─────────────────┐
│ [Antenna 2]     │
│    ↓  ↓  ↓      │
│ ┌───┬───┬───┐   │
│ │ ⬡ │ ⬡ │ ⬡ │   │  ← RFID tags on spice containers
│ ├───┼───┼───┤   │
│ │ ⬡ │ ⬡ │ ⬡ │   │
│ └───┴───┴───┘   │
└─────────────────┘
```

**"Put It Back" guidance:**

1. RFID detects container removed from Antenna 1 zone
2. RGB strip lights that zone RED
3. System logs removal, camera captures fill level
4. When container returns (RFID detected approaching):
   - RGB pulses BLUE at original position
   - User guided to correct spot
5. Container placed back → GREEN confirmation
6. Wrong spot? → YELLOW warning + BLUE at correct spot

### Laser Encoder System (Can Rotation)

For the FIFO can dispenser on V2 Shelf 2:

```
CAN ROTATION - SIDE VIEW (per lane)
───────────────────────────────────

   LOAD (back)                    DISPENSE (front)
        │                              │
        ▼                              ▼
   ┌─────────────────────────────────────┐
   │ ●  ●  ●  ●  ●  ●  ●  ●  ●  ●   ║   │──→ [IR Beam OUT]
   │                                 ║   │         │
   │    Cans roll toward front      ║   │         ▼
   │         (gravity fed)          ║   │    Count: OUT
   └─────────────────────────────────────┘
       ↑
   [IR Beam IN]
       │
       ▼
   Count: IN

   Current inventory = IN count - OUT count
```

**Multi-lane setup:**

```
TOP VIEW - 6-LANE CAN ROTATION
──────────────────────────────

┌──────┬──────┬──────┬──────┬──────┬──────┐
│Tomato│Beans │ Corn │Broth │Soup  │Tuna  │
│      │      │      │      │      │      │
│[IR]  │[IR]  │[IR]  │[IR]  │[IR]  │[IR]  │ ← OUT sensors (front)
│  ●●● │  ●●  │ ●●●● │  ●   │ ●●●  │  ●●  │
│  ●●● │  ●●  │ ●●●● │  ●   │ ●●●  │  ●●  │
│  ●●  │  ●   │ ●●●  │      │ ●●   │  ●   │
│[IR]  │[IR]  │[IR]  │[IR]  │[IR]  │[IR]  │ ← IN sensors (back)
└──────┴──────┴──────┴──────┴──────┴──────┘
   6       4      10     2      7      4    ← Current count

Low stock alert: Broth (2 cans) ⚠️
```

### Wiring Architecture

```
WIRING RUNS THROUGH STEEL TUBING
────────────────────────────────

V1 (Left Ladder):
├── USB power (to ESP32-CAMs for shelves 1, 2, 3)
├── RGB data line (directly driven by ESP32-CAM GPIO)
├── RFID antenna cable (Shelf 1 → runs to central reader)
└── All ESP32-CAMs connect via WiFi (power only through tube)

V2 (Middle Ladder):
├── USB power (to ESP32-CAMs for shelves 1, 3)
├── USB power (to ESP32 for can rotation laser system)
├── RGB data lines
└── IR sensor wiring (12 sensors for 6-lane can system)

V3 (Right Ladder - Spice Tower):
├── USB power (to ESP32-CAM for spice tower + pouch bin)
├── RGB data line
├── RFID antenna cable → runs to central reader
└── Camera for pouch bin (barcode scanning)

CENTRAL JUNCTION BOX (floor level, behind pantry):
├── UHF RFID Reader (4-port)
├── Powered USB Hub (10-port)
├── Power distribution
└── Single USB run to Raspberry Pi at display location
```

### Cable Specifications

| Cable Type | Length | Purpose |
|------------|--------|---------|
| USB 2.0 extension (6ft) | × 8 | Power to ESP32-CAMs and ESP32s |
| Coax (RG-58 or LMR-195) | 15ft × 2 | RFID antennas to reader |
| 2-conductor 22AWG | 30ft | IR sensor wiring |
| 3-conductor 22AWG | 20ft | RGB LED data + power |
| Cat6 ethernet (optional) | 10ft | Pi to reader if not USB |

### Pre-Installation Checklist

**Before welding/assembly:**
- [ ] Drill wire pass-through holes at shelf heights (1/2")
- [ ] Drill holes at bottom of each vertical tube for cable exit
- [ ] Plan RFID antenna mounting positions (back of shelf, aimed forward)
- [ ] Verify cable lengths with 20% extra

**During frame assembly:**
- [ ] Pull cables through tubes BEFORE welding cross-braces
- [ ] Leave 12" service loops at each shelf level
- [ ] Label all cable ends
- [ ] Install conduit or cable guides for antenna coax
- [ ] Take photos of wiring before closing up

**After frame complete:**
- [ ] Test continuity on all wires
- [ ] Mount ESP32-CAMs at each shelf (angled down)
- [ ] Mount RFID antennas (back of shelf, facing forward)
- [ ] Install RGB strips (front edge of each shelf)
- [ ] Install IR sensors at can rotation lanes
- [ ] Test each system individually before integration

### Junction Box Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                      JUNCTION BOX                                │
│                    (behind pantry at floor level)                │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  UHF RFID    │  │  USB Hub     │  │  Power Strip         │  │
│  │  Reader      │  │  (10-port)   │  │  (surge protected)   │  │
│  │  (4-port)    │  │              │  │                      │  │
│  │              │  │  To ESP32s:  │  │  ┌──┐ ┌──┐ ┌──┐     │  │
│  │  Ant1: Bulk  │  │  • V1 Cam×3  │  │  │  │ │  │ │  │     │  │
│  │  Ant2: Spice │  │  • V2 Cam×2  │  │  └──┘ └──┘ └──┘     │  │
│  │  Ant3: spare │  │  • V2 Laser  │  │                      │  │
│  │  Ant4: spare │  │  • V3 Cam×2  │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│         │                  │                    │               │
│         └──────────────────┼────────────────────┘               │
│                            │                                     │
│                   USB to Raspberry Pi                            │
│                   (single cable to display area)                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Hardware Integration Specifications

### Weight Sensor System

**Hardware per sensor node:**
- ESP32 microcontroller
- HX711 load cell amplifier
- 4x 50kg load cells (wired in full bridge)
- 5V power supply

**Communication:**
- ESP32 connects to Pi via WiFi
- MQTT for real-time weight updates
- Fallback: HTTP POST to API

**Data flow:**
```
Load cells → HX711 → ESP32 → WiFi/MQTT → Pi → Database
```

**ESP32 behavior:**
1. Read weight continuously (every 100ms)
2. Apply smoothing (rolling average)
3. Detect stable weight (variance < threshold for 2 seconds)
4. On significant change (>10g delta from last stable), publish event
5. Include: sensor_id, weight_before, weight_after, timestamp

**Calibration process:**
1. Place known weight on sensor
2. API endpoint records raw value and actual weight
3. Calculate scale factor
4. Store in database and push to ESP32

### Pouch Camera System

**Hardware:**
- Raspberry Pi Camera Module 3 (or USB webcam)
- LED strip for consistent lighting
- Mounted above pouch bin, angled to see items passing through

**Software flow:**
```
Camera feed → Motion detection → Frame capture → 
Barcode decode (pyzbar) → Product lookup → Inventory update
```

**Detection logic:**
1. Continuous low-res monitoring for motion
2. Motion detected → capture high-res frames
3. Attempt barcode decode on each frame
4. If barcode found:
   - Lookup product in database
   - Compare to last known state
   - Log addition or removal
5. If no barcode but product recognized (via Claude Vision):
   - Lower confidence score
   - May prompt user to confirm

**Handling unknown barcodes:**
1. Query Open Food Facts API
2. If found, create product automatically
3. If not found, prompt user to identify via touchscreen

### Freezer Inventory System

The freezer presents unique challenges: items get buried, frost obscures labels, and there's no good way to passively monitor what's inside. The solution is a **photo-based inventory system** with AI recognition.

**Hardware:**
- Camera mounted inside freezer door (or handheld for manual scans)
- Optional: small display on freezer door showing current contents
- Cold-rated camera or external camera with view window

**Two Approaches:**

**Option A: Door-Mounted Camera (Passive)**
```
Freezer door opens → Camera captures interior → 
AI identifies visible items → Updates inventory → 
Compares to last state → Detects additions/removals
```

Challenges:
- Frost/fog on lens
- Items buried behind others
- Lighting inside freezer

**Option B: "Scan Before You Store" (Semi-Manual)**
```
User adds item to freezer → Quick barcode scan or photo →
System logs item with timestamp → 
User removes item → Tap to confirm removal on touchscreen
```

This is more reliable and also captures:
- Date frozen (for tracking freezer burn risk)
- What the item actually is (not just "mystery foil package")

**Recommended Hybrid Approach:**

1. **On entry:** Quick scan/photo when items go IN the freezer
   - Barcode scan if packaged
   - Photo + description if homemade ("leftover chili, 1/25/26")
   - Voice note option ("two pounds ground beef")

2. **Periodic audit:** Monthly "freezer inventory" prompt
   - System asks: "Do you still have these items?"
   - User confirms or removes from list
   - Optional: take fresh photo of freezer contents for AI review

3. **Smart prompts:** When recipes call for frozen items
   - "This recipe needs frozen corn — you added some on 12/15. Still have it?"

**Database additions for freezer:**

```sql
-- Freezer-specific fields added to inventory table
ALTER TABLE inventory ADD COLUMN frozen_date DATE;
ALTER TABLE inventory ADD COLUMN freeze_by_date DATE;
ALTER TABLE inventory ADD COLUMN thaw_instructions TEXT;
ALTER TABLE inventory ADD COLUMN container_description TEXT;  -- "red lid container", "foil wrapped"

-- Freezer audit log
CREATE TABLE freezer_audits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    photo_path TEXT,
    items_confirmed INTEGER,
    items_removed INTEGER,
    notes TEXT
);
```

**UI: Freezer Section**

```
┌────────────────────────────────────────────────────────────────────┐
│  ← Back              FREEZER                      [📷 Audit]       │
├────────────────────────────────────────────────────────────────────┤
│  [All] [Meat] [Vegetables] [Prepared] [Oldest First]              │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ⚠️  OLDEST ITEMS (consider using soon)                           │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ 🟡  Ground Beef (2 lbs)              Frozen: Oct 15, 2025   │  │
│  │     "Blue freezer bag, bottom drawer"         98 days ago   │  │
│  │ 🟡  Leftover Chili                   Frozen: Nov 2, 2025    │  │
│  │     "Red lid tupperware"                      85 days ago   │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  MEAT & PROTEIN                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ 🟢  Chicken Breasts (4)              Frozen: Jan 10, 2026   │  │
│  │ 🟢  Pork Chops (6)                   Frozen: Jan 18, 2026   │  │
│  │ 🟡  Ground Beef (2 lbs)              Frozen: Oct 15, 2025   │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  VEGETABLES                                                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ 🟢  Frozen Corn (2 bags)             Frozen: Dec 20, 2025   │  │
│  │ 🟢  Mixed Vegetables                 Frozen: Jan 5, 2026    │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    ➕ ADD TO FREEZER                          │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

**"Add to Freezer" Flow:**

```
┌────────────────────────────────────────────────────────────────────┐
│  ← Back            ADD TO FREEZER                                  │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  What are you freezing?                                           │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  🔍  Search or scan barcode...                               │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  QUICK ADD                                                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐             │
│  │ Ground  │  │ Chicken │  │ Leftover│  │  Soup   │             │
│  │  Beef   │  │ Breast  │  │  Meal   │  │         │             │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘             │
│                                                                    │
│  ─────────────────────────────────────────────────────────────── │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  📷  TAKE PHOTO                                              │  │
│  │  Snap a picture of what you're freezing                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  🎤  VOICE NOTE                                              │  │
│  │  "Two pounds ground beef in blue bag"                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

**Freezer Item Detail (after selection):**

```
┌────────────────────────────────────────────────────────────────────┐
│  ← Back            ADD TO FREEZER                                  │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Ground Beef                                                       │
│                                                                    │
│  Quantity:    [ 2 ]  lbs                                          │
│                                                                    │
│  Where is it? (helps you find it later)                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Blue freezer bag, bottom drawer                             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  Photo (optional):  [📷 Add Photo]                                │
│                                                                    │
│  ─────────────────────────────────────────────────────────────── │
│                                                                    │
│        ┌────────────────────────────────────────────┐             │
│        │              ADD TO FREEZER                 │             │
│        └────────────────────────────────────────────┘             │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

**Freezer Audit Flow:**

Triggered monthly (or manually):

```
┌────────────────────────────────────────────────────────────────────┐
│              FREEZER AUDIT - January 2026                          │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Let's make sure your freezer inventory is accurate.              │
│  Tap items you NO LONGER have:                                    │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ ☑️  Ground Beef (2 lbs) - Oct 15                 [REMOVE]    │  │
│  │ ☑️  Chicken Breasts (4) - Jan 10                [KEEP]      │  │
│  │ ☑️  Leftover Chili - Nov 2                      [REMOVE]    │  │
│  │ ☑️  Pork Chops (6) - Jan 18                     [KEEP]      │  │
│  │ ☑️  Frozen Corn (2 bags) - Dec 20               [KEEP]      │  │
│  │ ☑️  Mixed Vegetables - Jan 5                    [KEEP]      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  Found something not listed?  [➕ Add Item]                        │
│                                                                    │
│  ─────────────────────────────────────────────────────────────── │
│                                                                    │
│        ┌────────────────────────────────────────────┐             │
│        │            COMPLETE AUDIT                   │             │
│        └────────────────────────────────────────────┘             │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

**Freezer Alerts:**

- "You have ground beef that's been frozen for 90+ days — use soon!"
- "Leftover chili from November — still good but consider using this week"
- "Monthly freezer audit due — take 2 minutes to verify contents"

**Recipe Integration:**

When suggesting meals, the system factors in:
- Frozen proteins that need to be used (oldest first)
- Thaw time requirements ("Chicken needs to thaw — start tomorrow for dinner")
- "You have frozen ground beef — here are 5 recipes that use it"

### Receipt Scanning

**Input methods:**
- Pi camera capture (touchscreen "take photo" button)
- File upload from phone (via web interface)

**Processing pipeline:**
```
Image → Claude API (vision) → Structured JSON → 
Product matching → User confirmation → Inventory update
```

**Claude API prompt for receipt parsing:**
```
Analyze this grocery receipt image. Extract all purchased items as JSON:
{
  "store_name": "string",
  "date": "YYYY-MM-DD",
  "items": [
    {
      "raw_text": "original text from receipt",
      "product_name": "normalized product name",
      "quantity": number,
      "unit_price": number,
      "total_price": number,
      "barcode": "if visible",
      "confidence": 0.0-1.0
    }
  ],
  "subtotal": number,
  "tax": number,
  "total": number
}
```

---

## Recipe Matching Algorithm

### Suggestion Scoring

```python
def calculate_recipe_score(recipe, inventory):
    """
    Returns tuple: (score, missing_required, missing_optional)
    Score: 0-100, higher = better match
    """
    required_ingredients = [i for i in recipe.ingredients if not i.is_optional]
    optional_ingredients = [i for i in recipe.ingredients if i.is_optional]
    
    required_have = 0
    required_missing = []
    
    for ingredient in required_ingredients:
        if ingredient.product_id:
            inv = get_inventory(ingredient.product_id)
            if inv and inv.quantity >= ingredient.quantity:
                required_have += 1
            else:
                required_missing.append(ingredient)
        else:
            # Untracked ingredient - assume we might have it
            required_have += 0.5
            
    optional_have = 0
    optional_missing = []
    
    for ingredient in optional_ingredients:
        if ingredient.product_id:
            inv = get_inventory(ingredient.product_id)
            if inv and inv.quantity >= ingredient.quantity:
                optional_have += 1
            else:
                optional_missing.append(ingredient)
    
    # Score calculation
    if len(required_ingredients) == 0:
        required_score = 100
    else:
        required_score = (required_have / len(required_ingredients)) * 100
    
    if len(optional_ingredients) == 0:
        optional_bonus = 0
    else:
        optional_bonus = (optional_have / len(optional_ingredients)) * 10
    
    final_score = required_score + optional_bonus
    
    return (final_score, required_missing, optional_missing)
```

### Suggestion Categories

1. **"Ready to make"** - Score = 100 (have all required ingredients)
2. **"Almost ready"** - Score >= 80 (missing 1-2 items)
3. **"Could make if you had..."** - Score >= 50
4. **"Need to shop for"** - Score < 50

---

## Development Phases

### Phase 1: Core Application (MVP)
**Goal:** Working touchscreen app with manual inventory management

**Tasks:**
- [ ] Set up Pi with Raspberry Pi OS
- [ ] Install Python, Node.js, SQLite
- [ ] Create database schema
- [ ] Build FastAPI backend with core endpoints
- [ ] Build Svelte frontend with three-button UI
- [ ] Implement manual add/use/view inventory
- [ ] Basic product database with manual entry
- [ ] Deploy and test on touchscreen

**Deliverables:**
- Functional touchscreen inventory app
- Can manually track items
- Basic category organization

### Phase 2: Recipe Integration
**Goal:** Recipe storage and meal suggestions

**Tasks:**
- [ ] Recipe database tables and API endpoints
- [ ] Manual recipe entry UI
- [ ] Recipe import from URL (web scraping)
- [ ] Recipe matching algorithm
- [ ] "Tonight's suggestions" on main screen
- [ ] "Make this" button that decrements inventory
- [ ] Shopping list generation from recipes

**Deliverables:**
- Recipe library with ingredient linking
- Meal suggestions based on inventory
- Shopping list functionality

### Phase 3: Receipt Scanning
**Goal:** Bulk inventory updates via receipt photos

**Tasks:**
- [ ] Camera integration for photo capture
- [ ] Claude API integration for receipt OCR
- [ ] Receipt parsing and product matching
- [ ] Confirmation UI for ambiguous items
- [ ] Automatic product creation for new items
- [ ] Receipt history/audit log

**Deliverables:**
- Scan receipt → review → confirm → inventory updated
- Learns new products from receipts

### Phase 4: Weight Sensors
**Goal:** Passive detection of inventory changes on shelves

**Tasks:**
- [ ] ESP32 firmware for weight sensing
- [ ] MQTT broker setup on Pi
- [ ] Sensor registration and calibration UI
- [ ] Weight event detection and logging
- [ ] User prompts for unresolved events
- [ ] Learning system (weight delta → likely product)

**Deliverables:**
- Sensors detect when items removed
- System prompts user to identify what was used
- Over time, auto-suggests based on weight patterns

### Phase 5: Pouch Camera
**Goal:** Automatic tracking of seasoning pouches

**Tasks:**
- [ ] Camera mount and lighting setup
- [ ] Motion detection pipeline
- [ ] Barcode scanning integration
- [ ] Product state tracking (present/absent)
- [ ] Automatic inventory updates
- [ ] Unknown barcode handling (API lookup, user prompt)

**Deliverables:**
- Pouches tracked automatically via camera
- No user interaction required for normal use

### Phase 6: Polish & Advanced Features
**Goal:** Refinement and nice-to-haves

**Tasks:**
- [ ] Voice integration ("Hey, do we have taco seasoning?")
- [ ] Mobile-responsive web interface
- [ ] Usage analytics and trends
- [ ] Expiration date tracking and alerts
- [ ] Multi-user support
- [ ] Backup/restore functionality
- [ ] Dark mode
- [ ] Performance optimization

---

## File Structure

```
pantrypal/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # SQLite connection and setup
│   ├── models/
│   │   ├── __init__.py
│   │   ├── product.py
│   │   ├── inventory.py
│   │   ├── freezer.py
│   │   ├── recipe.py
│   │   ├── sensor.py
│   │   └── shopping.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── products.py
│   │   ├── inventory.py
│   │   ├── freezer.py
│   │   ├── recipes.py
│   │   ├── sensors.py
│   │   ├── receipts.py
│   │   └── shopping.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── barcode_lookup.py   # External barcode API
│   │   ├── receipt_parser.py   # Claude API integration
│   │   ├── recipe_matcher.py   # Suggestion algorithm
│   │   ├── weight_processor.py # Weight event handling
│   │   └── pouch_watcher.py    # Camera monitoring
│   ├── hardware/
│   │   ├── __init__.py
│   │   ├── camera.py           # Pi camera interface
│   │   ├── mqtt_client.py      # Weight sensor communication
│   │   └── barcode_scanner.py  # pyzbar wrapper
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── routes/
│   │   │   ├── +page.svelte        # Main screen
│   │   │   ├── inventory/
│   │   │   │   └── +page.svelte
│   │   │   ├── use/
│   │   │   │   └── +page.svelte
│   │   │   ├── add/
│   │   │   │   └── +page.svelte
│   │   │   ├── freezer/
│   │   │   │   ├── +page.svelte    # Freezer inventory
│   │   │   │   ├── add/
│   │   │   │   │   └── +page.svelte # Add to freezer
│   │   │   │   └── audit/
│   │   │   │       └── +page.svelte # Freezer audit flow
│   │   │   ├── recipes/
│   │   │   │   ├── +page.svelte
│   │   │   │   └── [id]/
│   │   │   │       └── +page.svelte
│   │   │   ├── shopping/
│   │   │   │   └── +page.svelte
│   │   │   └── settings/
│   │   │       └── +page.svelte
│   │   ├── lib/
│   │   │   ├── components/
│   │   │   │   ├── Header.svelte
│   │   │   │   ├── ProductCard.svelte
│   │   │   │   ├── RecipeCard.svelte
│   │   │   │   ├── FreezerItemCard.svelte
│   │   │   │   ├── AlertBanner.svelte
│   │   │   │   ├── BarcodeScanner.svelte
│   │   │   │   └── ReceiptConfirm.svelte
│   │   │   ├── stores/
│   │   │   │   ├── inventory.js
│   │   │   │   ├── freezer.js
│   │   │   │   ├── recipes.js
│   │   │   │   └── alerts.js
│   │   │   └── api.js          # Backend API client
│   │   ├── app.html
│   │   └── app.css             # Tailwind imports
│   ├── static/
│   ├── package.json
│   ├── svelte.config.js
│   ├── tailwind.config.js
│   └── vite.config.js
├── esp32/
│   └── weight_sensor/
│       ├── weight_sensor.ino   # Arduino sketch
│       └── config.h            # WiFi credentials, MQTT broker
├── scripts/
│   ├── setup.sh                # Initial Pi setup
│   ├── deploy.sh               # Deployment script
│   └── backup.sh               # Database backup
├── data/
│   └── pantrypal.db            # SQLite database
├── docker-compose.yml          # Optional containerization
└── README.md
```

---

## Configuration

### Environment Variables (.env)

```bash
# Database
DATABASE_PATH=/home/pi/pantrypal/data/pantrypal.db

# Claude API (for receipt scanning)
ANTHROPIC_API_KEY=sk-ant-xxxxx

# MQTT (for weight sensors)
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USERNAME=pantrypal
MQTT_PASSWORD=xxxxx

# External APIs
OPEN_FOOD_FACTS_ENABLED=true

# Hardware
POUCH_CAMERA_ENABLED=true
POUCH_CAMERA_DEVICE=/dev/video0
WEIGHT_SENSORS_ENABLED=true

# Server
API_HOST=0.0.0.0
API_PORT=8000
```

---

## Getting Started Commands

```bash
# Clone and setup
cd /home/pi
mkdir pantrypal && cd pantrypal

# Backend setup
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy aiosqlite python-multipart pyzbar opencv-python anthropic paho-mqtt pillow

# Frontend setup
cd frontend
npm create svelte@latest .
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Initialize database
cd ../backend
python -c "from database import init_db; init_db()"

# Run development
# Terminal 1:
cd backend && uvicorn main:app --reload --host 0.0.0.0

# Terminal 2:
cd frontend && npm run dev -- --host 0.0.0.0
```

---

## Notes for Claude Code

1. **Start with Phase 1** - Get the core app working before adding hardware
2. **Test on desktop first** - Build and iterate faster, then deploy to Pi
3. **Mobile-first CSS** - Touchscreen is the primary interface
4. **Big touch targets** - Buttons should be minimum 48px, ideally 64px+
5. **Error handling everywhere** - Hardware fails, APIs timeout, handle gracefully
6. **Offline capability** - Core functions should work without internet
7. **Logging** - Extensive logging for debugging hardware issues
8. **Database migrations** - Plan for schema changes as features are added

---

## Success Criteria

- [ ] Kids can grab stuff without any interaction and system eventually learns
- [ ] Receipt scan adds 10+ items in under 60 seconds
- [ ] "What can I make for dinner?" answered in under 3 seconds
- [ ] System runs 24/7 without crashes
- [ ] Touchscreen UI is responsive and intuitive
- [ ] Shopping list generates automatically from low stock + planned recipes
- [ ] Freezer inventory stays accurate with monthly audits
- [ ] Old freezer items get surfaced in recipe suggestions before they go bad
- [ ] Adding items to freezer takes under 30 seconds
