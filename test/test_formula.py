from __future__ import unicode_literals


def test_dummy_formula(File):
    assert File("/hello_salt").content == "hi\n"
