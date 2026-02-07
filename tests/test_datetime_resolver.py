def test_datetime_resolution_case(case, resolver):
    result = resolver.resolve(
        filename=case["filename"],
        exif_datetime=case["exif_datetime"],
        fs_modified=case["fs_modified"],
    )

    assert result.datetime.isoformat() == case["expected"]["datetime"]
    assert result.source == case["expected"]["source"]
    assert result.confidence == case["expected"]["confidence"]
