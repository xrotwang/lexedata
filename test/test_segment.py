import re

from lexedata.edit.add_segments import segment_form, SegmentReport


def test_unkown_aspiration(caplog):
    form = "-á:muaʰ"
    segment_form(form, SegmentReport())
    print(caplog.text)
    assert re.search("Unknown sound aʰ encountered in -á:muaʰ", caplog.text)


def test_segment_report():
    report = SegmentReport()
    report.sounds["aʰ"]["count"] = 1
    report.sounds["aʰ"]["comment"] = "comment"
    report = report("language")
    assert report == [("language", "aʰ", 1, "comment")]


def test_unknown_sound(caplog):
    form = "wohuᵈnasi"
    segment_form(form, SegmentReport())
    print(caplog.text)
    assert re.search("Unknown sound uᵈ encountered in wohuᵈnasi", caplog.text)
