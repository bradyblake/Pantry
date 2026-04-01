// Product types
export interface Product {
	id: number;
	barcode: string | null;
	name: string;
	category: string | null;
	subcategory: string | null;
	default_unit: string;
	default_quantity: number;
	shelf_life_days: number | null;
	image_url: string | null;
	created_at: string;
	updated_at: string;
}

export interface ProductCreate {
	name: string;
	barcode?: string | null;
	category?: string | null;
	subcategory?: string | null;
	default_unit?: string;
	default_quantity?: number;
	shelf_life_days?: number | null;
	image_url?: string | null;
}

export interface ProductUpdate {
	name?: string;
	barcode?: string | null;
	category?: string | null;
	subcategory?: string | null;
	default_unit?: string;
	default_quantity?: number;
	shelf_life_days?: number | null;
	image_url?: string | null;
}

// Freezer types
export interface Freezer {
	id: number;
	name: string;
	location: string | null;
	description: string | null;
	created_at: string;
}

export interface FreezerCreate {
	name: string;
	location?: string | null;
	description?: string | null;
}

export interface FreezerUpdate {
	name?: string;
	location?: string | null;
	description?: string | null;
}

// Inventory types
export interface ProductInInventory {
	id: number;
	name: string;
	category: string | null;
	default_unit: string;
}

export interface FreezerInInventory {
	id: number;
	name: string;
	location: string | null;
}

export interface InventoryItem {
	id: number;
	product_id: number;
	quantity: number;
	location: string | null;
	expiration_date: string | null;
	freezer_id: number | null;
	frozen_date: string | null;
	freeze_by_date: string | null;
	container_description: string | null;
	photo_path: string | null;
	updated_at: string;
	product: ProductInInventory;
	freezer: FreezerInInventory | null;
}

export interface InventoryAdd {
	product_id: number;
	quantity: number;
	location?: string;
	expiration_date?: string | null;
	notes?: string | null;
	freezer_id?: number | null;
	frozen_date?: string | null;
	freeze_by_date?: string | null;
	container_description?: string | null;
}

export interface InventoryUse {
	product_id: number;
	quantity: number;
	notes?: string | null;
}

export interface InventoryUpdate {
	quantity?: number;
	location?: string;
	expiration_date?: string | null;
	freezer_id?: number | null;
	frozen_date?: string | null;
	freeze_by_date?: string | null;
	container_description?: string | null;
}

export interface InventoryLog {
	id: number;
	product_id: number;
	quantity_change: number;
	source: string;
	confidence: number;
	notes: string | null;
	created_at: string;
	product: ProductInInventory;
}

// Shopping list types
export interface ProductInShopping {
	id: number;
	name: string;
	category: string | null;
	default_unit: string;
}

export interface ShoppingItem {
	id: number;
	product_id: number | null;
	custom_item_name: string | null;
	quantity: number | null;
	unit: string | null;
	checked: boolean;
	added_reason: string | null;
	created_at: string;
	product: ProductInShopping | null;
}

export interface ShoppingItemCreate {
	product_id?: number | null;
	custom_item_name?: string | null;
	quantity?: number | null;
	unit?: string | null;
	added_reason?: string;
}

export interface ShoppingItemUpdate {
	product_id?: number | null;
	custom_item_name?: string | null;
	quantity?: number | null;
	unit?: string | null;
	checked?: boolean;
}

// Utility types
export type StockLevel = 'high' | 'low' | 'out';

export function getStockLevel(quantity: number, threshold: number = 1): StockLevel {
	if (quantity <= 0) return 'out';
	if (quantity <= threshold) return 'low';
	return 'high';
}

export function getDaysFrozen(frozenDate: string | null): number | null {
	if (!frozenDate) return null;
	const frozen = new Date(frozenDate);
	const today = new Date();
	const diffTime = Math.abs(today.getTime() - frozen.getTime());
	return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

// Recipe types
export interface ProductInRecipe {
	id: number;
	name: string;
	category: string | null;
	default_unit: string;
}

export interface RecipeIngredient {
	id: number;
	recipe_id: number;
	product_id: number | null;
	ingredient_text: string;
	quantity: number | null;
	unit: string | null;
	is_optional: boolean;
	notes: string | null;
	product: ProductInRecipe | null;
}

export interface RecipeIngredientCreate {
	ingredient_text: string;
	product_id?: number | null;
	quantity?: number | null;
	unit?: string | null;
	is_optional?: boolean;
	notes?: string | null;
}

export interface RecipeDocument {
	id: number;
	filename: string;
	original_filename: string;
	file_type: string;
	file_size_bytes: number | null;
	page_count: number | null;
	parsed: boolean;
	parsed_at: string | null;
	parse_error: string | null;
	created_at: string;
}

export interface Recipe {
	id: number;
	name: string;
	description: string | null;
	instructions: string | null;
	prep_time_minutes: number | null;
	cook_time_minutes: number | null;
	servings: number | null;
	source: string | null;
	source_url: string | null;
	source_document_id: number | null;
	image_url: string | null;
	tags: string | null;
	created_at: string;
	updated_at: string;
	ingredients: RecipeIngredient[];
	source_document: RecipeDocument | null;
}

export interface RecipeCreate {
	name: string;
	description?: string | null;
	instructions?: string | null;
	prep_time_minutes?: number | null;
	cook_time_minutes?: number | null;
	servings?: number | null;
	source?: string;
	source_url?: string | null;
	image_url?: string | null;
	tags?: string | null;
	ingredients?: RecipeIngredientCreate[];
}

export interface RecipeUpdate {
	name?: string;
	description?: string | null;
	instructions?: string | null;
	prep_time_minutes?: number | null;
	cook_time_minutes?: number | null;
	servings?: number | null;
	source_url?: string | null;
	image_url?: string | null;
	tags?: string | null;
}

export interface RecipeSuggestion {
	recipe: Recipe;
	score: number;
	missing_required: RecipeIngredient[];
	missing_optional: RecipeIngredient[];
	status: 'ready' | 'almost_ready' | 'need_items' | 'need_shopping';
}

// Helper to parse tags JSON
export function parseTags(tagsJson: string | null): string[] {
	if (!tagsJson) return [];
	try {
		return JSON.parse(tagsJson);
	} catch {
		return [];
	}
}

// Zone types
export interface Zone {
	id: number;
	name: string;
	location: string | null;
	description: string | null;
	esp32_id: string | null;
	led_strip_index: number;
	rfid_antenna_id: number | null;
	zone_type: string;
	display_order: number;
	current_led_state: string;
	led_color: string | null;
	created_at: string;
	updated_at: string;
}

export interface ZoneCreate {
	name: string;
	location?: string | null;
	description?: string | null;
	esp32_id?: string | null;
	led_strip_index?: number;
	rfid_antenna_id?: number | null;
	zone_type?: string;
	display_order?: number;
}

export type LedState = 'off' | 'idle' | 'scanning' | 'confirm' | 'success' | 'return' | 'add' | 'highlight';

export interface LedCommand {
	state: LedState;
	color?: string | null;
	duration_ms?: number | null;
	pulse?: boolean;
}

// RFID types
export interface RfidTag {
	id: number;
	tag_id: string;
	product_id: number | null;
	container_name: string | null;
	home_zone_id: number | null;
	current_zone_id: number | null;
	is_present: boolean;
	is_out: boolean;
	removed_at: string | null;
	last_seen_at: string | null;
	created_at: string;
	home_zone: { id: number; name: string; location: string | null } | null;
	current_zone: { id: number; name: string; location: string | null } | null;
	product: { id: number; name: string; category: string | null } | null;
}

export interface RfidTagCreate {
	tag_id: string;
	product_id?: number | null;
	container_name?: string | null;
	home_zone_id?: number | null;
}

export interface PutItBackAlert {
	tag_id: number;
	tag_epc: string;
	product_name: string | null;
	container_name: string | null;
	home_zone_id: number;
	home_zone_name: string;
	home_zone_location: string | null;
	current_zone_id: number | null;
	current_zone_name: string | null;
	removed_at: string | null;
	minutes_out: number;
}

// Ingredient finder types
export interface InventoryEntryInfo {
	quantity: number;
	location: string | null;
	container_description: string | null;
	freezer_name: string | null;
}

export interface IngredientLocation {
	ingredient_text: string;
	product_id: number | null;
	product_name: string | null;
	zone_id: number | null;
	zone_name: string | null;
	zone_location: string | null;
	in_stock: boolean;
	quantity_available: number;
	inventory_entries: InventoryEntryInfo[];
}

export interface FindIngredientsResponse {
	recipe_id: number;
	recipe_name: string;
	ingredients: IngredientLocation[];
	zones_to_light: number[];
	missing_ingredients: string[];
	message: string;
}
