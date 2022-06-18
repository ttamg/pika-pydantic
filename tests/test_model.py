def test_models_encode_and_decode(TestData):

    data = TestData(value=5, elements=["a", "b"])

    encoded = data.encode()
    assert encoded == b'{"value": 5, "elements": ["a", "b"]}'

    decoded = TestData.decode(encoded)
    assert decoded == {"value": 5, "elements": ["a", "b"]}
