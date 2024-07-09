from re import compile

MAD_FINDER = compile(pattern=r"\bmad\b")


def test__mad_reactor_returns_true() -> None:
    """
    This test should find if the word mad returns
    """
    test_sentence = "I was very mad about tiny mans"

    is_mad = MAD_FINDER.findall(string=test_sentence)
    assert bool(is_mad) is True


def test__mad_reactor_returns_false() -> None:
    """
    This test should test if the letters in the test
    return when in other words
    """
    test_sentence = "I made this myself"

    is_mad = MAD_FINDER.findall(string=test_sentence)
    assert bool(is_mad) is False
