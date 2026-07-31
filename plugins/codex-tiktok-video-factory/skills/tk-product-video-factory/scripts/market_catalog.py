"""Verified TikTok Shop market and language defaults.

Sources are recorded because TikTok's help pages and regional launch announcements
do not always update at the same time.
"""

VERIFIED_AT = "2026-07-31"
SOURCES = [
    "https://ads.tiktok.com/help/article/tiktok-shopping-and-showcase",
    "https://newsroom.tiktok.com/tiktok-shop-expands-across-europe",
]
VOICE_BY_LOCALE = {
    "en-PH": {"female": "en-PH-RosaNeural", "male": "en-PH-JamesNeural"},
    "en-SG": {"female": "en-SG-LunaNeural", "male": "en-SG-WayneNeural"},
    "fr-BE": {"female": "fr-BE-CharlineNeural", "male": "fr-BE-GerardNeural"},
    "ms-MY": {"female": "ms-MY-YasminNeural", "male": "ms-MY-OsmanNeural"},
    "nl-BE": {"female": "nl-BE-DenaNeural", "male": "nl-BE-ArnaudNeural"},
    "ta-SG": {"female": "ta-SG-VenbaNeural", "male": "ta-SG-AnbuNeural"},
    "zh-CN": {"female": "zh-CN-XiaoxiaoNeural", "male": "zh-CN-YunxiNeural"},
}


def market(name, language, locale, currency, female, male, *, languages=None, source="help-center"):
    VOICE_BY_LOCALE.setdefault(locale, {"female": female, "male": male})
    return {
        "name": name,
        "language": language,
        "locale": locale,
        "currency": currency,
        "voices": {"female": female, "male": male},
        "languages": languages or [{"language": language, "locale": locale}],
        "source_group": source,
    }


MARKETS = {
    # Asia-Pacific
    "ID": market("印度尼西亚", "印尼语", "id-ID", "IDR", "id-ID-GadisNeural", "id-ID-ArdiNeural"),
    "JP": market("日本", "日语", "ja-JP", "JPY", "ja-JP-NanamiNeural", "ja-JP-KeitaNeural"),
    "MY": market("马来西亚", "马来语", "ms-MY", "MYR", "ms-MY-YasminNeural", "ms-MY-OsmanNeural",
                 languages=[{"language": "马来语", "locale": "ms-MY"}, {"language": "英语", "locale": "en-SG"}, {"language": "中文", "locale": "zh-CN"}]),
    "PH": market("菲律宾", "菲律宾语", "fil-PH", "PHP", "fil-PH-BlessicaNeural", "fil-PH-AngeloNeural",
                 languages=[{"language": "菲律宾语", "locale": "fil-PH"}, {"language": "英语", "locale": "en-PH"}]),
    "SG": market("新加坡", "英语", "en-SG", "SGD", "en-SG-LunaNeural", "en-SG-WayneNeural",
                 languages=[{"language": "英语", "locale": "en-SG"}, {"language": "中文", "locale": "zh-CN"}, {"language": "马来语", "locale": "ms-MY"}, {"language": "泰米尔语", "locale": "ta-SG"}]),
    "TH": market("泰国", "泰语", "th-TH", "THB", "th-TH-PremwadeeNeural", "th-TH-NiwatNeural"),
    "VN": market("越南", "越南语", "vi-VN", "VND", "vi-VN-HoaiMyNeural", "vi-VN-NamMinhNeural"),
    # Americas
    "BR": market("巴西", "葡萄牙语", "pt-BR", "BRL", "pt-BR-FranciscaNeural", "pt-BR-AntonioNeural"),
    "MX": market("墨西哥", "西班牙语", "es-MX", "MXN", "es-MX-DaliaNeural", "es-MX-JorgeNeural"),
    "US": market("美国", "英语", "en-US", "USD", "en-US-AvaNeural", "en-US-AndrewNeural"),
    # Europe: help-center and official 2026 expansion announcement
    "FR": market("法国", "法语", "fr-FR", "EUR", "fr-FR-DeniseNeural", "fr-FR-HenriNeural"),
    "IE": market("爱尔兰", "英语", "en-IE", "EUR", "en-IE-EmilyNeural", "en-IE-ConnorNeural"),
    "IT": market("意大利", "意大利语", "it-IT", "EUR", "it-IT-ElsaNeural", "it-IT-DiegoNeural"),
    "ES": market("西班牙", "西班牙语", "es-ES", "EUR", "es-ES-ElviraNeural", "es-ES-AlvaroNeural"),
    "GB": market("英国", "英语", "en-GB", "GBP", "en-GB-SoniaNeural", "en-GB-RyanNeural"),
    "DE": market("德国", "德语", "de-DE", "EUR", "de-DE-KatjaNeural", "de-DE-ConradNeural", source="official-newsroom"),
    "AT": market("奥地利", "德语", "de-AT", "EUR", "de-AT-IngridNeural", "de-AT-JonasNeural", source="official-newsroom"),
    "BE": market("比利时", "荷兰语", "nl-BE", "EUR", "nl-BE-DenaNeural", "nl-BE-ArnaudNeural",
                 languages=[{"language": "荷兰语", "locale": "nl-BE"}, {"language": "法语", "locale": "fr-BE"}], source="official-newsroom"),
    "NL": market("荷兰", "荷兰语", "nl-NL", "EUR", "nl-NL-FennaNeural", "nl-NL-MaartenNeural", source="official-newsroom"),
    "PL": market("波兰", "波兰语", "pl-PL", "PLN", "pl-PL-ZofiaNeural", "pl-PL-MarekNeural", source="official-newsroom"),
}
