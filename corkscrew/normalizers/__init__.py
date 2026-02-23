from corkscrew.normalizers.farr_vintners import FarrVintnersNormalizer
from corkscrew.normalizers.hub_wine import HubWineNormalizer
from corkscrew.normalizers.google_sheets import GoogleSheetsNormalizer

# Map merchant_id → normalizer class
MERCHANT_NORMALIZER_MAP = {
    "farr-vintners": FarrVintnersNormalizer,
    # hub.wine merchants
    "sterling-fine-wines": HubWineNormalizer,
    "bibo-wine": HubWineNormalizer,
    "decorum-vintners": HubWineNormalizer,
    "falcon-vintners": HubWineNormalizer,
    "grand-vin-wm": HubWineNormalizer,
    # Google Sheets merchants
    "turville-valley-wines": GoogleSheetsNormalizer,
    "cave-de-chaz": GoogleSheetsNormalizer,
    "burgundy-cave": GoogleSheetsNormalizer,
}
