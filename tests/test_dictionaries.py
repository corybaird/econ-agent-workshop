from references.dictionaries.dict_country_converter import dict_country


def test_country_codes_are_plain_keys():
    for mapping in dict_country.values():
        for key, value in mapping.items():
            assert not set("^$|\\") & set(key + value), (key, value)


def test_country_aliases():
    iso3 = dict_country["iso2_to_iso3"]
    assert iso3["GB"] == iso3["UK"] == "GBR"
    assert iso3["GR"] == iso3["EL"] == "GRC"
    assert iso3["NA"] == "NAM"


def test_iso3_round_trip():
    for iso3, iso2 in dict_country["iso3_to_iso2"].items():
        assert dict_country["iso2_to_iso3"][iso2] == iso3
