from corkscrew.normalizer import XLSXNormalizer

class HubWineNormalizer(XLSXNormalizer):
    DEFAULT_COLUMN_MAP = {
        "Wine Name": "wine_name",
        "Vintage": "vintage",
        "Region": "region",
        "Appellation": "appellation",
        "Colour": "color",
        "Format": "format",
        "Price": "price",
        "Currency": "currency",
        "Stock": "stock_quantity",
        "Case Size": "case_size",
    }

    def normalize(self, filepath, merchant, download_date):
        if not merchant.column_map:
            import copy
            patched = copy.copy(merchant)
            object.__setattr__(patched, "column_map", self.DEFAULT_COLUMN_MAP)
            return super().normalize(filepath, patched, download_date)
        return super().normalize(filepath, merchant, download_date)
