from corkscrew.normalizer import CSVNormalizer

class FarrVintnersNormalizer(CSVNormalizer):
    DEFAULT_COLUMN_MAP = {
        "Wine": "wine_name",
        "Vintage": "vintage",
        "Region": "region",
        "Appellation": "appellation",
        "Colour": "color",
        "Format": "format",
        "Price (ex VAT)": "price",
        "Currency": "currency",
        "Stock": "stock_quantity",
        "Case Size": "case_size",
        "Score": "score",
        "Scorer": "scorer",
        "Condition": "condition_notes",
    }

    def normalize(self, filepath, merchant, download_date):
        # Use config column_map if provided, otherwise fall back to default
        if not merchant.column_map:
            import copy
            patched = copy.copy(merchant)
            object.__setattr__(patched, "column_map", self.DEFAULT_COLUMN_MAP)
            return super().normalize(filepath, patched, download_date)
        return super().normalize(filepath, merchant, download_date)
