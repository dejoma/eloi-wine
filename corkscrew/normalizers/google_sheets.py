from corkscrew.normalizer import CSVNormalizer

class GoogleSheetsNormalizer(CSVNormalizer):
    """Generic normalizer for Google Sheets exports.
    Column map must be provided in merchants.yaml for each sheet merchant.
    """
    pass  # Inherits all CSV behavior; column_map from config
