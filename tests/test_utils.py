from util import pretty_string_to_bool


def test_pretty_string_to_bool_passed_bool():
    assert pretty_string_to_bool(True)
    assert not pretty_string_to_bool(False)


def test_pretty_string_to_bool_passed_short_string():
    assert pretty_string_to_bool("y")
    assert pretty_string_to_bool("Y")
    assert pretty_string_to_bool("t")
    assert pretty_string_to_bool("T")
    assert not pretty_string_to_bool("n")


def test_pretty_string_to_bool_passed_true_false_string():
    assert pretty_string_to_bool("true")
    assert pretty_string_to_bool("True")
    assert pretty_string_to_bool("TRUE")
    assert not pretty_string_to_bool("false")
    assert not pretty_string_to_bool("False")
    assert not pretty_string_to_bool("FALSE")


def test_pretty_string_to_bool_passed_yes():
    assert pretty_string_to_bool("yes")
    assert pretty_string_to_bool("YES")
    assert pretty_string_to_bool("Yes")
    assert not pretty_string_to_bool("nu")
    assert not pretty_string_to_bool("NO")
    assert not pretty_string_to_bool("No")


def test_pretty_string_to_bool_passed_misc():
    assert not pretty_string_to_bool("a")
    assert not pretty_string_to_bool("b")
    assert not pretty_string_to_bool("C")
    assert not pretty_string_to_bool("D")
    assert not pretty_string_to_bool("e")
    assert not pretty_string_to_bool("ffffff")


def test_pretty_string_to_bool_passed_int():
    assert pretty_string_to_bool(1)
    assert pretty_string_to_bool(2)
    assert pretty_string_to_bool(1000)
    assert pretty_string_to_bool(-1)
    assert pretty_string_to_bool(-2)
    assert pretty_string_to_bool(-500)
    assert not pretty_string_to_bool(0)

