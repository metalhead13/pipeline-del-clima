from weather_pipeline.transform import raw_document_to_frame


def test_transform_adds_metadata_and_indicators(raw_document, thresholds):
    frame = raw_document_to_frame(raw_document, thresholds)
    assert len(frame) == 2
    assert frame.loc[0, "city"] == "bogota"
    assert not bool(frame.loc[0, "is_rainy_day"])
    assert bool(frame.loc[1, "is_heavy_rain_day"])
    assert bool(frame.loc[1, "is_strong_wind_day"])
    assert bool(frame.loc[1, "is_adverse_day"])
    assert frame.loc[1, "temperature_range_c"] == 12.0
