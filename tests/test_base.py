#!/usr/bin/env python
# coding=utf-8
"""
该测试用例来源于python源码，删除了enum部分去掉的功能测试用例；
"""
from __future__ import print_function

import inspect
import unittest
from test import support
from datetime import timedelta
from collections import OrderedDict
from pickle import dumps, loads, PicklingError, HIGHEST_PROTOCOL

import six

from py_enum import enum
from py_enum.enum import Enum, unique, EnumMeta

try:
    import threading
except ImportError:
    threading = None

# for pickle tests
try:
    class Stooges(Enum):
        LARRY = 1
        CURLY = 2
        MOE = 3
except Exception as exc:
    Stooges = exc

try:
    class IntStooges(int, Enum):
        LARRY = 1
        CURLY = 2
        MOE = 3
except Exception as exc:
    IntStooges = exc

try:
    class FloatStooges(float, Enum):
        LARRY = 1.39
        CURLY = 2.72
        MOE = 3.142596
except Exception as exc:
    FloatStooges = exc

# for pickle test and subclass tests
try:
    class StrEnum(str, Enum):
        'accepts only string values'

    class Name(StrEnum):
        BDFL = 'Guido van Rossum'
        FLUFL = 'Barry Warsaw'
except Exception as exc:
    Name = exc

try:
    Question = Enum('Question', 'who what when where why', module=__name__)
except Exception as exc:
    Question = exc

try:
    Answer = Enum('Answer', 'him this then there because')
except Exception as exc:
    Answer = exc

try:
    Theory = Enum('Theory', 'rule law supposition', qualname='spanish_inquisition')
except Exception as exc:
    Theory = exc

# for doctests
try:
    class Fruit(Enum):
        TOMATO = 1
        BANANA = 2
        CHERRY = 3
except Exception:
    pass


def _test_pickle_dump_load(assertion, source, target=None):
    if target is None:
        target = source
    for protocol in range(HIGHEST_PROTOCOL + 1):
        assertion(loads(dumps(source, protocol=protocol)), target)


def _test_pickle_exception(assertion, exception, obj):
    for protocol in range(HIGHEST_PROTOCOL + 1):
        with assertion(exception):
            dumps(obj, protocol=protocol)


class TestHelpers(unittest.TestCase):
    # _is_descriptor, _is_sunder, _is_dunder

    def test_is_descriptor(self):
        class foo:
            pass

        for attr in ('__get__', '__set__', '__delete__'):
            obj = foo()
            self.assertFalse(enum._is_descriptor(obj))
            setattr(obj, attr, 1)
            self.assertTrue(enum._is_descriptor(obj))

    def test_is_sunder(self):
        for s in ('_a_', '_aa_'):
            self.assertTrue(enum._is_sunder(s))

        for s in ('a', 'a_', '_a', '__a', 'a__', '__a__', '_a__', '__a_', '_',
                  '__', '___', '____', '_____',):
            self.assertFalse(enum._is_sunder(s))

    def test_is_dunder(self):
        for s in ('__a__', '__aa__'):
            self.assertTrue(enum._is_dunder(s))
        for s in ('a', 'a_', '_a', '__a', 'a__', '_a_', '_a__', '__a_', '_',
                  '__', '___', '____', '_____',):
            self.assertFalse(enum._is_dunder(s))


# tests

class TestEnum(unittest.TestCase):

    def setUp(self):
        class Season(Enum):
            SPRING = 1
            SUMMER = 2
            AUTUMN = 3
            WINTER = 4

        self.Season = Season

        class Konstants(float, Enum):
            E = 2.7182818
            PI = 3.1415926
            TAU = 2 * PI

        self.Konstants = Konstants

        class Directional(str, Enum):
            EAST = 'east'
            WEST = 'west'
            NORTH = 'north'
            SOUTH = 'south'

        self.Directional = Directional

        from datetime import date

        class Holiday(date, Enum):
            NEW_YEAR = 2013, 1, 1
            IDES_OF_MARCH = 2013, 3, 15

        self.Holiday = Holiday

    def test_dir_on_class(self):
        Season = self.Season
        self.assertEqual(
            set(dir(Season)),
            {'__class__', '__doc__', '__members__', '__module__', 'SPRING', 'SUMMER', 'AUTUMN', 'WINTER'},
        )

    def test_dir_on_item(self):
        Season = self.Season
        self.assertEqual(
            set(dir(Season.WINTER)),
            {'__class__', '__doc__', '__module__', 'name', 'value'},
        )

    def test_dir_with_added_behavior(self):
        class Test(Enum):
            this = 'that'
            these = 'those'

            def wowser(self):
                return "Wowser! I'm %s!" % self.name

        self.assertEqual(
            set(dir(Test)),
            {'__class__', '__doc__', '__members__', '__module__', 'this', 'these'},
        )
        self.assertEqual(
            set(dir(Test.this)),
            {'__class__', '__doc__', '__module__', 'name', 'value', 'wowser'},
        )

    def test_dir_on_sub_with_behavior_on_super(self):
        # see issue22506
        class SuperEnum(Enum):
            def invisible(self):
                return "did you see me?"

        class SubEnum(SuperEnum):
            sample = 5

        self.assertEqual(
            set(dir(SubEnum.sample)),
            {'__class__', '__doc__', '__module__', 'name', 'value', 'invisible'},
        )

    def test_enum_in_enum_out(self):
        Season = self.Season
        self.assertIs(Season(Season.WINTER), Season.WINTER)

    def test_enum_value(self):
        Season = self.Season
        self.assertEqual(Season.SPRING.value, 1)

    def test_intenum_value(self):
        self.assertEqual(IntStooges.CURLY.value, 2)

    def test_enum(self):
        Season = self.Season
        lst = list(Season)
        self.assertEqual(len(lst), len(Season))
        self.assertEqual(len(Season), 4, Season)
        if not six.PY2:
            self.assertEqual(
                [Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER], lst)

        for i, season in enumerate('SPRING SUMMER AUTUMN WINTER'.split(), 1):
            e = Season(i)
            self.assertEqual(e, getattr(Season, season))
            self.assertEqual(e.value, i)
            self.assertNotEqual(e, i)
            self.assertEqual(e.name, season)
            self.assertIn(e, Season)
            self.assertIs(type(e), Season)
            self.assertIsInstance(e, Season)
            self.assertEqual(str(e), 'Season.' + season)
            self.assertEqual(
                repr(e),
                '<Season.{0}: {1}>'.format(season, i),
            )

    def test_value_name(self):
        Season = self.Season
        self.assertEqual(Season.SPRING.name, 'SPRING')
        self.assertEqual(Season.SPRING.value, 1)
        with self.assertRaises(AttributeError):
            Season.SPRING.name = 'invierno'
        with self.assertRaises(AttributeError):
            Season.SPRING.value = 2

    def test_changing_member(self):
        Season = self.Season
        with self.assertRaises(AttributeError):
            Season.WINTER = 'really cold'

    def test_attribute_deletion(self):
        class Season(Enum):
            SPRING = 1
            SUMMER = 2
            AUTUMN = 3
            WINTER = 4

            def spam(cls):
                pass

        self.assertTrue(hasattr(Season, 'spam'))
        del Season.spam
        self.assertFalse(hasattr(Season, 'spam'))

        with self.assertRaises(AttributeError):
            del Season.SPRING
        with self.assertRaises(AttributeError):
            del Season.DRY
        with self.assertRaises(AttributeError):
            del Season.SPRING.name

    def test_bool_of_class(self):
        # python2没有定义__bool__，按照__len__计算
        class Empty(Enum):
            pass

        if not six.PY2:
            self.assertTrue(bool(Empty))
        else:
            self.assertFalse(bool(Empty))

    def test_bool_of_member(self):
        class Count(Enum):
            zero = 0
            one = 1
            two = 2

        for member in Count:
            self.assertTrue(bool(member))

    def test_invalid_names(self):
        with self.assertRaises(ValueError):
            class Wrong(Enum):
                mro = 9
        with self.assertRaises(ValueError):
            class Wrong2(Enum):
                _create_ = 11
        with self.assertRaises(ValueError):
            class Wrong3(Enum):
                _get_mixins_ = 9
        with self.assertRaises(ValueError):
            class Wrong4(Enum):
                _find_new_ = 1
        with self.assertRaises(ValueError):
            class Wrong5(Enum):
                _any_name_ = 9

    def test_bool(self):
        # plain Enum members are always True
        class Logic(Enum):
            true = True
            false = False

        self.assertTrue(Logic.true)
        self.assertTrue(Logic.false)

        # unless overridden
        class RealLogic(Enum):
            true = True
            false = False

            def __bool__(self):
                return bool(self._value_)

        if not six.PY2:
            self.assertTrue(RealLogic.true)
            self.assertFalse(RealLogic.false)

        # mixed Enums depend on mixed-in type
        class IntLogic(int, Enum):
            true = 1
            false = 0

        self.assertTrue(IntLogic.true)
        self.assertFalse(IntLogic.false)

    def test_contains(self):
        Season = self.Season
        self.assertIn(Season.AUTUMN, Season)
        if not six.PY2:
            with self.assertWarns(DeprecationWarning):
                self.assertNotIn(3, Season)
            with self.assertWarns(DeprecationWarning):
                self.assertNotIn('AUTUMN', Season)

        val = Season(3)
        self.assertIn(val, Season)

        class OtherEnum(Enum):
            one = 1
            two = 2

        self.assertNotIn(OtherEnum.two, Season)

    def test_member_contains(self):
        self.assertRaises(TypeError, lambda: 'test' in self.Season.AUTUMN)
        self.assertRaises(TypeError, lambda: 3 in self.Season.AUTUMN)
        self.assertRaises(TypeError, lambda: 'AUTUMN' in self.Season.AUTUMN)

    def test_comparisons(self):
        # python2可以直接对比,但对比关系不明确
        if not six.PY2:
            Season = self.Season
            with self.assertRaises(TypeError):
                Season.SPRING < Season.WINTER
            with self.assertRaises(TypeError):
                Season.SPRING > 4

            self.assertNotEqual(Season.SPRING, 1)

            class Part(Enum):
                SPRING = 1
                CLIP = 2
                BARREL = 3

            self.assertNotEqual(Season.SPRING, Part.SPRING)
            with self.assertRaises(TypeError):
                Season.SPRING < Part.CLIP

    def test_enum_duplicates(self):
        class Season(Enum):
            SPRING = 1
            SUMMER = 2
            AUTUMN = FALL = 3
            WINTER = 4
            ANOTHER_SPRING = 1

        lst = list(Season)
        if not six.PY2:
            self.assertEqual(
                lst,
                [Season.SPRING, Season.SUMMER,
                 Season.AUTUMN, Season.WINTER,
                 ])
            self.assertEqual(Season.FALL.name, 'AUTUMN')
            self.assertEqual(
                [k for k, v in Season.__members__.items() if v.name != k],
                ['FALL', 'ANOTHER_SPRING'],
            )
        self.assertIs(Season.FALL, Season.AUTUMN)
        self.assertEqual(Season.FALL.value, 3)
        self.assertEqual(Season.AUTUMN.value, 3)
        self.assertIs(Season(3), Season.AUTUMN)
        self.assertIs(Season(1), Season.SPRING)

    def test_duplicate_name(self):
        # Python2属性初始化无法识别多个相同的Key
        if not six.PY2:
            with self.assertRaises(TypeError):
                class Color(Enum):
                    red = 1
                    green = 2
                    blue = 3
                    red = 4

            with self.assertRaises(TypeError):
                class Color2(Enum):
                    red = 1
                    green = 2
                    blue = 3

                    def red(self):
                        return 'red'

            with self.assertRaises(TypeError):
                class Color3(Enum):
                    @property
                    def red(self):
                        return 'redder'

                    red = 1  # type: ignore # noqa: F811
                    green = 2
                    blue = 3

    def test_enum_with_value_name(self):
        class Huh(Enum):
            name = 1
            value = 2

        if not six.PY2:
            self.assertEqual(
                list(Huh),
                [Huh.name, Huh.value],
            )
        self.assertIs(type(Huh.name), Huh)
        self.assertEqual(Huh.name.name, 'name')
        self.assertEqual(Huh.name.value, 1)

    def test_format_enum(self):
        Season = self.Season
        self.assertEqual('{}'.format(Season.SPRING),
                         '{}'.format(str(Season.SPRING)))
        self.assertEqual('{:}'.format(Season.SPRING),
                         '{:}'.format(str(Season.SPRING)))
        self.assertEqual('{:20}'.format(Season.SPRING),
                         '{:20}'.format(str(Season.SPRING)))
        self.assertEqual('{:^20}'.format(Season.SPRING),
                         '{:^20}'.format(str(Season.SPRING)))
        self.assertEqual('{:>20}'.format(Season.SPRING),
                         '{:>20}'.format(str(Season.SPRING)))
        self.assertEqual('{:<20}'.format(Season.SPRING),
                         '{:<20}'.format(str(Season.SPRING)))

    def test_format_enum_custom(self):
        class TestFloat(float, Enum):
            one = 1.0
            two = 2.0

            def __format__(self, spec):
                return 'TestFloat success!'

        self.assertEqual('{}'.format(TestFloat.one), 'TestFloat success!')

    def assertFormatIsValue(self, spec, member):
        self.assertEqual(spec.format(member), spec.format(member.value))

    def test_format_enum_date(self):
        Holiday = self.Holiday
        self.assertFormatIsValue('{}', Holiday.IDES_OF_MARCH)
        self.assertFormatIsValue('{:}', Holiday.IDES_OF_MARCH)
        self.assertFormatIsValue('{:20}', Holiday.IDES_OF_MARCH)
        self.assertFormatIsValue('{:^20}', Holiday.IDES_OF_MARCH)
        self.assertFormatIsValue('{:>20}', Holiday.IDES_OF_MARCH)
        self.assertFormatIsValue('{:<20}', Holiday.IDES_OF_MARCH)
        self.assertFormatIsValue('{:%Y %m}', Holiday.IDES_OF_MARCH)
        self.assertFormatIsValue('{:%Y %m %M:00}', Holiday.IDES_OF_MARCH)

    def test_format_enum_float(self):
        Konstants = self.Konstants
        self.assertFormatIsValue('{}', Konstants.TAU)
        self.assertFormatIsValue('{:}', Konstants.TAU)
        self.assertFormatIsValue('{:20}', Konstants.TAU)
        self.assertFormatIsValue('{:^20}', Konstants.TAU)
        self.assertFormatIsValue('{:>20}', Konstants.TAU)
        self.assertFormatIsValue('{:<20}', Konstants.TAU)
        self.assertFormatIsValue('{:n}', Konstants.TAU)
        self.assertFormatIsValue('{:5.2}', Konstants.TAU)
        self.assertFormatIsValue('{:f}', Konstants.TAU)

    def test_format_enum_str(self):
        Directional = self.Directional
        self.assertFormatIsValue('{}', Directional.WEST)
        self.assertFormatIsValue('{:}', Directional.WEST)
        self.assertFormatIsValue('{:20}', Directional.WEST)
        self.assertFormatIsValue('{:^20}', Directional.WEST)
        self.assertFormatIsValue('{:>20}', Directional.WEST)
        self.assertFormatIsValue('{:<20}', Directional.WEST)

    def test_hash(self):
        Season = self.Season
        dates = {}
        dates[Season.WINTER] = '1225'
        dates[Season.SPRING] = '0315'
        dates[Season.SUMMER] = '0704'
        dates[Season.AUTUMN] = '1031'
        self.assertEqual(dates[Season.AUTUMN], '1031')

    def test_intenum_from_scratch(self):
        class phy(int, Enum):
            pi = 3
            tau = 2 * pi

        self.assertTrue(phy.pi < phy.tau)

    def test_intenum_inherited(self):
        class IntEnum(int, Enum):
            pass

        class phy(IntEnum):
            pi = 3
            tau = 2 * pi

        self.assertTrue(phy.pi < phy.tau)

    def test_floatenum_from_scratch(self):
        class phy(float, Enum):
            pi = 3.1415926
            tau = 2 * pi

        self.assertTrue(phy.pi < phy.tau)

    def test_floatenum_inherited(self):
        class FloatEnum(float, Enum):
            pass

        class phy(FloatEnum):
            pi = 3.1415926
            tau = 2 * pi

        self.assertTrue(phy.pi < phy.tau)

    def test_strenum_from_scratch(self):
        class phy(str, Enum):
            pi = 'Pi'
            tau = 'Tau'

        self.assertTrue(phy.pi < phy.tau)

    def test_strenum_inherited(self):
        class StrEnum(str, Enum):
            pass

        class phy(StrEnum):
            pi = 'Pi'
            tau = 'Tau'

        self.assertTrue(phy.pi < phy.tau)

    def test_floatenum_fromhex(self):
        h = float.hex(FloatStooges.MOE.value)
        self.assertIs(FloatStooges.fromhex(h), FloatStooges.MOE)
        h = float.hex(FloatStooges.MOE.value + 0.01)
        with self.assertRaises(ValueError):
            FloatStooges.fromhex(h)

    def test_pickle_enum(self):
        if isinstance(Stooges, Exception):
            raise Stooges
        _test_pickle_dump_load(self.assertIs, Stooges.CURLY)
        _test_pickle_dump_load(self.assertIs, Stooges)

    def test_pickle_int(self):
        if isinstance(IntStooges, Exception):
            raise IntStooges
        _test_pickle_dump_load(self.assertIs, IntStooges.CURLY)
        _test_pickle_dump_load(self.assertIs, IntStooges)

    def test_pickle_float(self):
        if isinstance(FloatStooges, Exception):
            raise FloatStooges
        _test_pickle_dump_load(self.assertIs, FloatStooges.CURLY)
        _test_pickle_dump_load(self.assertIs, FloatStooges)

    def test_pickle_enum_function(self):
        if isinstance(Answer, Exception):
            raise Answer
        _test_pickle_dump_load(self.assertIs, Answer.him)
        _test_pickle_dump_load(self.assertIs, Answer)

    def test_pickle_enum_function_with_module(self):
        if isinstance(Question, Exception):
            raise Question
        _test_pickle_dump_load(self.assertIs, Question.who)
        _test_pickle_dump_load(self.assertIs, Question)

    def test_enum_function_with_qualname(self):
        if isinstance(Theory, Exception):
            raise Theory
        self.assertEqual(Theory.__qualname__, 'spanish_inquisition')

    def test_class_nested_enum_and_pickle_protocol_four(self):
        if not six.PY2:
            # would normally just have this directly in the class namespace
            class NestedEnum(Enum):
                twigs = 'common'
                shiny = 'rare'

            self.__class__.NestedEnum = NestedEnum
            self.NestedEnum.__qualname__ = '%s.NestedEnum' % self.__class__.__name__
            _test_pickle_dump_load(self.assertIs, self.NestedEnum.twigs)

    def test_exploding_pickle(self):
        BadPickle = Enum(
            'BadPickle', 'dill sweet bread-n-butter', module=__name__)
        globals()['BadPickle'] = BadPickle
        # now break BadPickle to test exception raising
        enum._make_class_unpicklable(BadPickle)
        _test_pickle_exception(self.assertRaises, TypeError, BadPickle.dill)
        _test_pickle_exception(self.assertRaises, PicklingError, BadPickle)

    def test_string_enum(self):
        class SkillLevel(str, Enum):
            master = 'what is the sound of one hand clapping?'
            journeyman = 'why did the chicken cross the road?'
            apprentice = 'knock, knock!'

        self.assertEqual(SkillLevel.apprentice, 'knock, knock!')

    def test_getattr_getitem(self):
        class Period(Enum):
            morning = 1
            noon = 2
            evening = 3
            night = 4

        self.assertIs(Period(2), Period.noon)
        self.assertIs(getattr(Period, 'night'), Period.night)
        self.assertIs(Period['morning'], Period.morning)

    def test_getattr_dunder(self):
        Season = self.Season
        self.assertTrue(getattr(Season, '__eq__'))

    def test_iteration_order(self):
        if not six.PY2:
            class Season(Enum):
                SUMMER = 2
                WINTER = 4
                AUTUMN = 3
                SPRING = 1

            self.assertEqual(
                list(Season),
                [Season.SUMMER, Season.WINTER, Season.AUTUMN, Season.SPRING],
            )

    def test_reversed_iteration_order(self):
        if not six.PY2:
            self.assertEqual(
                list(reversed(self.Season)),
                [self.Season.WINTER, self.Season.AUTUMN, self.Season.SUMMER,
                 self.Season.SPRING]
            )

    def test_programmatic_function_string(self):
        SummerMonth = Enum('SummerMonth', 'june july august')
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        if not six.PY2:
            self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
            )
        for i, month in enumerate('june july august'.split(), 1):
            e = SummerMonth(i)
            self.assertEqual(int(e.value), i)
            self.assertNotEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    def test_programmatic_function_string_with_start(self):
        SummerMonth = Enum('SummerMonth', 'june july august', start=10)
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        if not six.PY2:
            self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
            )
        for i, month in enumerate('june july august'.split(), 10):
            e = SummerMonth(i)
            self.assertEqual(int(e.value), i)
            self.assertNotEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    def test_programmatic_function_string_list(self):
        SummerMonth = Enum('SummerMonth', ['june', 'july', 'august'])
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        if not six.PY2:
            self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
            )
        for i, month in enumerate('june july august'.split(), 1):
            e = SummerMonth(i)
            self.assertEqual(int(e.value), i)
            self.assertNotEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    def test_programmatic_function_string_list_with_start(self):
        SummerMonth = Enum('SummerMonth', ['june', 'july', 'august'], start=20)
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        if not six.PY2:
            self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
            )
        for i, month in enumerate('june july august'.split(), 20):
            e = SummerMonth(i)
            self.assertEqual(int(e.value), i)
            self.assertNotEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    def test_programmatic_function_iterable(self):
        SummerMonth = Enum(
            'SummerMonth',
            (('june', 1), ('july', 2), ('august', 3))
        )
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        if not six.PY2:
            self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
            )
        for i, month in enumerate('june july august'.split(), 1):
            e = SummerMonth(i)
            self.assertEqual(int(e.value), i)
            self.assertNotEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    def test_programmatic_function_from_dict(self):
        SummerMonth = Enum(
            'SummerMonth',
            OrderedDict((('june', 1), ('july', 2), ('august', 3)))
        )
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        if not six.PY2:
            self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
            )
        for i, month in enumerate('june july august'.split(), 1):
            e = SummerMonth(i)
            self.assertEqual(int(e.value), i)
            self.assertNotEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    def test_programmatic_function_type(self):
        SummerMonth = Enum('SummerMonth', 'june july august', type=int)
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        if not six.PY2:
            self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
            )
        for i, month in enumerate('june july august'.split(), 1):
            e = SummerMonth(i)
            self.assertEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    def test_programmatic_function_type_with_start(self):
        SummerMonth = Enum('SummerMonth', 'june july august', type=int, start=30)
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        if not six.PY2:
            self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
            )
        for i, month in enumerate('june july august'.split(), 30):
            e = SummerMonth(i)
            self.assertEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    def test_subclassing(self):
        if isinstance(Name, Exception):
            raise Name
        self.assertEqual(Name.BDFL, 'Guido van Rossum')
        self.assertTrue(Name.BDFL, Name('Guido van Rossum'))
        self.assertIs(Name.BDFL, getattr(Name, 'BDFL'))
        _test_pickle_dump_load(self.assertIs, Name.BDFL)

    def test_extending(self):
        class Color(Enum):
            red = 1
            green = 2
            blue = 3

        with self.assertRaises(TypeError):
            class MoreColor(Color):
                cyan = 4
                magenta = 5
                yellow = 6

    def test_exclude_methods(self):
        class whatever(Enum):
            this = 'that'
            these = 'those'

            def really(self):
                return 'no, not %s' % self.value

        self.assertIsNot(type(whatever.really), whatever)
        self.assertEqual(whatever.this.really(), 'no, not that')

    def test_wrong_inheritance_order(self):
        with self.assertRaises(TypeError):
            class Wrong(Enum, str):
                NotHere = 'error before this point'

    def test_wrong_enum_in_call(self):
        class Monochrome(Enum):
            black = 0
            white = 1

        class Gender(Enum):
            male = 0
            female = 1

        self.assertRaises(ValueError, Monochrome, Gender.male)

    def test_flufl_enum(self):
        class Fluflnum(Enum):
            def __int__(self):
                return int(self.value)

        class MailManOptions(Fluflnum):
            option1 = 1
            option2 = 2
            option3 = 3

        self.assertEqual(int(MailManOptions.option1), 1)

    def test_no_such_enum_member(self):
        class Color(Enum):
            red = 1
            green = 2
            blue = 3

        with self.assertRaises(ValueError):
            Color(4)
        with self.assertRaises(KeyError):
            Color['chartreuse']

    def test_new_repr(self):
        class Color(Enum):
            red = 1
            green = 2
            blue = 3

            def __repr__(self):
                return "don't you just love shades of %s?" % self.name

        self.assertEqual(
            repr(Color.blue),
            "don't you just love shades of blue?",
        )

    def test_inherited_repr(self):
        class MyEnum(Enum):
            def __repr__(self):
                return "My name is %s." % self.name

        class MyIntEnum(int, MyEnum):
            this = 1
            that = 2
            theother = 3

        self.assertEqual(repr(MyIntEnum.that), "My name is that.")

    def test_subclasses_with_getnewargs(self):
        class NamedInt(int):
            __qualname__ = 'NamedInt'  # needed for pickle protocol 4

            def __new__(cls, *args):
                _args = args
                name = args[0]
                args = args[1:]
                if len(args) == 0:
                    raise TypeError("name and value must be specified")
                self = int.__new__(cls, *args)
                self._intname = name
                self._args = _args
                return self

            def __getnewargs__(self):
                return self._args

            @property
            def __name__(self):
                return self._intname

            def __repr__(self):
                # repr() is updated to include the name and type info
                return "{}({!r}, {})".format(type(self).__name__,
                                             self.__name__,
                                             int.__repr__(self))

            def __str__(self):
                # str() is unchanged, even if it relies on the repr() fallback
                base = int
                base_str = base.__str__
                if base_str.__objclass__ is object:
                    return base.__repr__(self)
                return base_str(self)

            # for simplicity, we only define one operator that
            # propagates expressions
            def __add__(self, other):
                temp = int(self) + int(other)
                if isinstance(self, NamedInt) and isinstance(other, NamedInt):
                    return NamedInt(
                        '({0} + {1})'.format(self.__name__, other.__name__),
                        temp)
                else:
                    return temp

        class NEI(NamedInt, Enum):
            __qualname__ = 'NEI'  # needed for pickle protocol 4
            x = ('the-x', 1)
            y = ('the-y', 2)

        self.assertIs(NEI.__new__, Enum.__new__)
        self.assertEqual(repr(NEI.x + NEI.y), "NamedInt('(the-x + the-y)', 3)")
        globals()['NamedInt'] = NamedInt
        globals()['NEI'] = NEI
        NI5 = NamedInt('test', 5)
        self.assertEqual(NI5, 5)
        _test_pickle_dump_load(self.assertEqual, NI5, 5)
        self.assertEqual(NEI.y.value, 2)
        _test_pickle_dump_load(self.assertIs, NEI.y)
        _test_pickle_dump_load(self.assertIs, NEI)

    def test_subclasses_with_getnewargs_ex(self):
        if not six.PY2:
            class NamedInt(int):
                __qualname__ = 'NamedInt'  # needed for pickle protocol 4

                def __new__(cls, *args):
                    _args = args
                    name = args[0]
                    args = args[1:]
                    if len(args) == 0:
                        raise TypeError("name and value must be specified")
                    self = int.__new__(cls, *args)
                    self._intname = name
                    self._args = _args
                    return self

                def __getnewargs_ex__(self):
                    return self._args, {}

                @property
                def __name__(self):
                    return self._intname

                def __repr__(self):
                    # repr() is updated to include the name and type info
                    return "{}({!r}, {})".format(type(self).__name__,
                                                 self.__name__,
                                                 int.__repr__(self))

                def __str__(self):
                    # str() is unchanged, even if it relies on the repr() fallback
                    base = int
                    base_str = base.__str__
                    if base_str.__objclass__ is object:
                        return base.__repr__(self)
                    return base_str(self)

                # for simplicity, we only define one operator that
                # propagates expressions
                def __add__(self, other):
                    temp = int(self) + int(other)
                    if isinstance(self, NamedInt) and isinstance(other, NamedInt):
                        return NamedInt(
                            '({0} + {1})'.format(self.__name__, other.__name__),
                            temp)
                    else:
                        return temp

            class NEI(NamedInt, Enum):
                __qualname__ = 'NEI'  # needed for pickle protocol 4
                x = ('the-x', 1)
                y = ('the-y', 2)

            self.assertIs(NEI.__new__, Enum.__new__)
            self.assertEqual(repr(NEI.x + NEI.y), "NamedInt('(the-x + the-y)', 3)")
            globals()['NamedInt'] = NamedInt
            globals()['NEI'] = NEI
            NI5 = NamedInt('test', 5)
            self.assertEqual(NI5, 5)
            _test_pickle_dump_load(self.assertEqual, NI5, 5)
            self.assertEqual(NEI.y.value, 2)
            _test_pickle_dump_load(self.assertIs, NEI.y)
            _test_pickle_dump_load(self.assertIs, NEI)

    def test_subclasses_with_reduce(self):
        class NamedInt(int):
            __qualname__ = 'NamedInt'  # needed for pickle protocol 4

            def __new__(cls, *args):
                _args = args
                name = args[0]
                args = args[1:]
                if len(args) == 0:
                    raise TypeError("name and value must be specified")
                self = int.__new__(cls, *args)
                self._intname = name
                self._args = _args
                return self

            def __reduce__(self):
                return self.__class__, self._args

            @property
            def __name__(self):
                return self._intname

            def __repr__(self):
                # repr() is updated to include the name and type info
                return "{}({!r}, {})".format(type(self).__name__,
                                             self.__name__,
                                             int.__repr__(self))

            def __str__(self):
                # str() is unchanged, even if it relies on the repr() fallback
                base = int
                base_str = base.__str__
                if base_str.__objclass__ is object:
                    return base.__repr__(self)
                return base_str(self)

            # for simplicity, we only define one operator that
            # propagates expressions
            def __add__(self, other):
                temp = int(self) + int(other)
                if isinstance(self, NamedInt) and isinstance(other, NamedInt):
                    return NamedInt(
                        '({0} + {1})'.format(self.__name__, other.__name__),
                        temp)
                else:
                    return temp

        class NEI(NamedInt, Enum):
            __qualname__ = 'NEI'  # needed for pickle protocol 4
            x = ('the-x', 1)
            y = ('the-y', 2)

        self.assertIs(NEI.__new__, Enum.__new__)
        self.assertEqual(repr(NEI.x + NEI.y), "NamedInt('(the-x + the-y)', 3)")
        globals()['NamedInt'] = NamedInt
        globals()['NEI'] = NEI
        NI5 = NamedInt('test', 5)
        self.assertEqual(NI5, 5)
        _test_pickle_dump_load(self.assertEqual, NI5, 5)
        self.assertEqual(NEI.y.value, 2)
        _test_pickle_dump_load(self.assertIs, NEI.y)
        _test_pickle_dump_load(self.assertIs, NEI)

    def test_subclasses_with_reduce_ex(self):
        if not six.PY2:
            class NamedInt(int):
                __qualname__ = 'NamedInt'  # needed for pickle protocol 4

                def __new__(cls, *args):
                    _args = args
                    name = args[0]
                    args = args[1:]
                    if len(args) == 0:
                        raise TypeError("name and value must be specified")
                    self = int.__new__(cls, *args)
                    self._intname = name
                    self._args = _args
                    return self

                def __reduce_ex__(self, proto):
                    return self.__class__, self._args

                @property
                def __name__(self):
                    return self._intname

                def __repr__(self):
                    # repr() is updated to include the name and type info
                    return "{}({!r}, {})".format(type(self).__name__,
                                                 self.__name__,
                                                 int.__repr__(self))

                def __str__(self):
                    # str() is unchanged, even if it relies on the repr() fallback
                    base = int
                    base_str = base.__str__
                    if base_str.__objclass__ is object:
                        return base.__repr__(self)
                    return base_str(self)

                # for simplicity, we only define one operator that
                # propagates expressions
                def __add__(self, other):
                    temp = int(self) + int(other)
                    if isinstance(self, NamedInt) and isinstance(other, NamedInt):
                        return NamedInt(
                            '({0} + {1})'.format(self.__name__, other.__name__),
                            temp)
                    else:
                        return temp

            class NEI(NamedInt, Enum):
                __qualname__ = 'NEI'  # needed for pickle protocol 4
                x = ('the-x', 1)
                y = ('the-y', 2)

            self.assertIs(NEI.__new__, Enum.__new__)
            self.assertEqual(repr(NEI.x + NEI.y), "NamedInt('(the-x + the-y)', 3)")
            globals()['NamedInt'] = NamedInt
            globals()['NEI'] = NEI
            NI5 = NamedInt('test', 5)
            self.assertEqual(NI5, 5)
            _test_pickle_dump_load(self.assertEqual, NI5, 5)
            self.assertEqual(NEI.y.value, 2)
            _test_pickle_dump_load(self.assertIs, NEI.y)
            _test_pickle_dump_load(self.assertIs, NEI)

    def test_subclasses_without_direct_pickle_support(self):
        class NamedInt(int):
            __qualname__ = 'NamedInt'

            def __new__(cls, *args):
                _args = args
                name = args[0]
                args = args[1:]
                if len(args) == 0:
                    raise TypeError("name and value must be specified")
                self = int.__new__(cls, *args)
                self._intname = name
                self._args = _args
                return self

            @property
            def __name__(self):
                return self._intname

            def __repr__(self):
                # repr() is updated to include the name and type info
                return "{}({!r}, {})".format(type(self).__name__,
                                             self.__name__,
                                             int.__repr__(self))

            def __str__(self):
                # str() is unchanged, even if it relies on the repr() fallback
                base = int
                base_str = base.__str__
                if base_str.__objclass__ is object:
                    return base.__repr__(self)
                return base_str(self)

            # for simplicity, we only define one operator that
            # propagates expressions
            def __add__(self, other):
                temp = int(self) + int(other)
                if isinstance(self, NamedInt) and isinstance(other, NamedInt):
                    return NamedInt(
                        '({0} + {1})'.format(self.__name__, other.__name__),
                        temp)
                else:
                    return temp

        class NEI(NamedInt, Enum):
            __qualname__ = 'NEI'
            x = ('the-x', 1)
            y = ('the-y', 2)

        self.assertIs(NEI.__new__, Enum.__new__)
        self.assertEqual(repr(NEI.x + NEI.y), "NamedInt('(the-x + the-y)', 3)")
        globals()['NamedInt'] = NamedInt
        globals()['NEI'] = NEI
        NI5 = NamedInt('test', 5)
        self.assertEqual(NI5, 5)
        self.assertEqual(NEI.y.value, 2)
        _test_pickle_exception(self.assertRaises, TypeError, NEI.x)
        _test_pickle_exception(self.assertRaises, PicklingError, NEI)

    def test_subclasses_without_direct_pickle_support_using_name(self):
        class NamedInt(int):
            __qualname__ = 'NamedInt'

            def __new__(cls, *args):
                _args = args
                name = args[0]
                args = args[1:]
                if len(args) == 0:
                    raise TypeError("name and value must be specified")
                self = int.__new__(cls, *args)
                self._intname = name
                self._args = _args
                return self

            @property
            def __name__(self):
                return self._intname

            def __repr__(self):
                # repr() is updated to include the name and type info
                return "{}({!r}, {})".format(type(self).__name__,
                                             self.__name__,
                                             int.__repr__(self))

            def __str__(self):
                # str() is unchanged, even if it relies on the repr() fallback
                base = int
                base_str = base.__str__
                if base_str.__objclass__ is object:
                    return base.__repr__(self)
                return base_str(self)

            # for simplicity, we only define one operator that
            # propagates expressions
            def __add__(self, other):
                temp = int(self) + int(other)
                if isinstance(self, NamedInt) and isinstance(other, NamedInt):
                    return NamedInt(
                        '({0} + {1})'.format(self.__name__, other.__name__),
                        temp)
                else:
                    return temp

        class NEI(NamedInt, Enum):
            __qualname__ = 'NEI'
            x = ('the-x', 1)
            y = ('the-y', 2)

            def __reduce_ex__(self, proto):
                return getattr, (self.__class__, self._name_)

        self.assertIs(NEI.__new__, Enum.__new__)
        self.assertEqual(repr(NEI.x + NEI.y), "NamedInt('(the-x + the-y)', 3)")
        globals()['NamedInt'] = NamedInt
        globals()['NEI'] = NEI
        NI5 = NamedInt('test', 5)
        self.assertEqual(NI5, 5)
        self.assertEqual(NEI.y.value, 2)
        _test_pickle_dump_load(self.assertIs, NEI.y)
        _test_pickle_dump_load(self.assertIs, NEI)

    def test_tuple_subclass(self):
        class SomeTuple(tuple, Enum):
            __qualname__ = 'SomeTuple'  # needed for pickle protocol 4
            first = (1, 'for the money')
            second = (2, 'for the show')
            third = (3, 'for the music')

        self.assertIs(type(SomeTuple.first), SomeTuple)
        self.assertIsInstance(SomeTuple.second, tuple)
        self.assertEqual(SomeTuple.third, (3, 'for the music'))
        globals()['SomeTuple'] = SomeTuple
        _test_pickle_dump_load(self.assertIs, SomeTuple.first)

    def test_duplicate_values_give_unique_enum_items(self):
        if not six.PY2:
            # Python2无法保证auto的顺序
            class AutoNumber(Enum):
                first = ()
                second = ()
                third = ()

                def __new__(cls):
                    value = len(cls.__members__) + 1
                    obj = object.__new__(cls)
                    obj._value_ = value
                    return obj

                def __int__(self):
                    return int(self._value_)

            self.assertEqual(
                list(AutoNumber),
                [AutoNumber.first, AutoNumber.second, AutoNumber.third],
            )
            self.assertEqual(int(AutoNumber.second), 2)
            self.assertEqual(AutoNumber.third.value, 3)
            self.assertIs(AutoNumber(1), AutoNumber.first)

    def test_inherited_new_from_enhanced_enum(self):
        if not six.PY2:
            class AutoNumber(Enum):
                def __new__(cls):
                    value = len(cls.__members__) + 1
                    obj = object.__new__(cls)
                    obj._value_ = value
                    return obj

                def __int__(self):
                    return int(self._value_)

            class Color(AutoNumber):
                red = ()
                green = ()
                blue = ()

            self.assertEqual(list(Color), [Color.red, Color.green, Color.blue])
            self.assertEqual(list(map(int, Color)), [1, 2, 3])

    def test_equality(self):
        class AlwaysEqual:
            def __eq__(self, other):
                return True

        class OrdinaryEnum(Enum):
            a = 1

        self.assertEqual(AlwaysEqual(), OrdinaryEnum.a)
        self.assertEqual(OrdinaryEnum.a, AlwaysEqual())

    def test_ordered_mixin(self):
        class OrderedEnum(Enum):
            def __ge__(self, other):
                if self.__class__ is other.__class__:
                    return self._value_ >= other._value_
                return NotImplemented

            def __gt__(self, other):
                if self.__class__ is other.__class__:
                    return self._value_ > other._value_
                return NotImplemented

            def __le__(self, other):
                if self.__class__ is other.__class__:
                    return self._value_ <= other._value_
                return NotImplemented

            def __lt__(self, other):
                if self.__class__ is other.__class__:
                    return self._value_ < other._value_
                return NotImplemented

        class Grade(OrderedEnum):
            A = 5
            B = 4
            C = 3
            D = 2
            F = 1

        self.assertGreater(Grade.A, Grade.B)
        self.assertLessEqual(Grade.F, Grade.C)
        self.assertLess(Grade.D, Grade.A)
        self.assertGreaterEqual(Grade.B, Grade.B)
        self.assertEqual(Grade.B, Grade.B)
        self.assertNotEqual(Grade.C, Grade.D)

    def test_extending2(self):
        class Shade(Enum):
            def shade(self):
                print(self.name)

        class Color(Shade):
            red = 1
            green = 2
            blue = 3

        with self.assertRaises(TypeError):
            class MoreColor(Color):
                cyan = 4
                magenta = 5
                yellow = 6

    def test_extending3(self):
        class Shade(Enum):
            def shade(self):
                return self.name

        class Color(Shade):
            def hex(self):
                return '%s hexlified!' % self.value

        class MoreColor(Color):
            cyan = 4
            magenta = 5
            yellow = 6

        self.assertEqual(MoreColor.magenta.hex(), '5 hexlified!')

    def test_subclass_duplicate_name(self):
        class Base(Enum):
            def test(self):
                pass

        class Test(Base):
            test = 1

        self.assertIs(type(Test.test), Test)

    def test_subclass_duplicate_name_dynamic(self):
        from py_enum.utils import DynamicClassAttribute

        class Base(Enum):
            @DynamicClassAttribute
            def test(self):
                return 'dynamic'

        class Test(Base):
            test = 1

        self.assertEqual(Test.test.test, 'dynamic')

    def test_no_duplicates(self):
        class UniqueEnum(Enum):
            def __init__(self, *args):
                cls = self.__class__
                if any(self.value == e.value for e in cls):
                    a = self.name
                    e = cls(self.value).name
                    raise ValueError(
                        "aliases not allowed in UniqueEnum:  %r --> %r"
                        % (a, e)
                    )

        class Color(UniqueEnum):
            red = 1
            green = 2
            blue = 3

        with self.assertRaises(ValueError):
            class Color2(UniqueEnum):
                red = 1
                green = 2
                blue = 3
                grene = 2

    def test_init(self):
        class Planet(Enum):
            MERCURY = (3.303e+23, 2.4397e6)
            VENUS = (4.869e+24, 6.0518e6)
            EARTH = (5.976e+24, 6.37814e6)
            MARS = (6.421e+23, 3.3972e6)
            JUPITER = (1.9e+27, 7.1492e7)
            SATURN = (5.688e+26, 6.0268e7)
            URANUS = (8.686e+25, 2.5559e7)
            NEPTUNE = (1.024e+26, 2.4746e7)

            def __init__(self, mass, radius):
                self.mass = mass  # in kilograms
                self.radius = radius  # in meters

            @property
            def surface_gravity(self):
                # universal gravitational constant  (m3 kg-1 s-2)
                G = 6.67300E-11
                return G * self.mass / (self.radius * self.radius)

        self.assertEqual(round(Planet.EARTH.surface_gravity, 2), 9.80)
        self.assertEqual(Planet.EARTH.value, (5.976e+24, 6.37814e6))

    def test_ignore(self):
        class Period(timedelta, Enum):
            '''
            different lengths of time
            '''

            def __new__(cls, value, period):
                obj = timedelta.__new__(cls, value)
                obj._value_ = value
                obj.period = period
                return obj

            _ignore_ = 'Period i'
            Period = vars()
            for i in range(13):
                Period['month_%d' % i] = i * 30, 'month'
            for i in range(53):
                Period['week_%d' % i] = i * 7, 'week'
            for i in range(32):
                Period['day_%d' % i] = i, 'day'
            OneDay = day_1  # type: ignore # noqa: F821
            OneWeek = week_1  # type: ignore # noqa: F821
            OneMonth = month_1  # type: ignore # noqa: F821

        self.assertFalse(hasattr(Period, '_ignore_'))
        self.assertFalse(hasattr(Period, 'Period'))
        self.assertFalse(hasattr(Period, 'i'))
        self.assertTrue(isinstance(Period.day_1, timedelta))
        self.assertTrue(Period.month_1 is Period.day_30)
        self.assertTrue(Period.week_4 is Period.day_28)

    def test_nonhash_value(self):
        if not six.PY2:
            class AutoNumberInAList(Enum):
                def __new__(cls):
                    value = [len(cls.__members__) + 1]
                    obj = object.__new__(cls)
                    obj._value_ = value
                    return obj

            class ColorInAList(AutoNumberInAList):
                red = ()
                green = ()
                blue = ()

            self.assertEqual(list(ColorInAList), [ColorInAList.red, ColorInAList.green, ColorInAList.blue])
            for instance, value in zip(ColorInAList, range(3)):
                value += 1
                self.assertEqual(instance.value, [value])
                self.assertIs(ColorInAList([value]), instance)

    def test_conflicting_types_resolved_in_new(self):
        if not six.PY2:
            class LabelledIntEnum(int, Enum):
                def __new__(cls, *args):
                    value, label = args
                    obj = int.__new__(cls, value)
                    obj.label = label
                    obj._value_ = value
                    return obj

            class LabelledList(LabelledIntEnum):
                unprocessed = (1, "Unprocessed")
                payment_complete = (2, "Payment Complete")

            self.assertEqual(list(LabelledList), [LabelledList.unprocessed, LabelledList.payment_complete])
            self.assertEqual(LabelledList.unprocessed, 1)
            self.assertEqual(LabelledList(1), LabelledList.unprocessed)

    def test_missing(self):
        class Color(Enum):
            red = 1
            green = 2
            blue = 3

            @classmethod
            def _missing_(cls, item):
                if item == 'three':
                    return cls.blue
                elif item == 'bad return':
                    # trigger internal error
                    return 5
                elif item == 'error out':
                    raise ZeroDivisionError
                else:
                    # trigger not found
                    return None

        self.assertIs(Color('three'), Color.blue)
        self.assertRaises(ValueError, Color, 7)
        try:
            Color('bad return')
        except TypeError as exc:
            self.assertTrue(isinstance(exc.__context__, ValueError))
        else:
            raise Exception('Exception not raised.')
        try:
            Color('error out')
        except ZeroDivisionError as exc:
            self.assertTrue(isinstance(exc.__context__, ValueError))
        else:
            raise Exception('Exception not raised.')

    def test_multiple_inherited_mixin(self):
        if not six.PY2:
            class StrEnum(str, Enum):
                def __new__(cls, *args, **kwargs):
                    for a in args:
                        if not isinstance(a, str):
                            raise TypeError("Enumeration '%s' (%s) is not"
                                            " a string" % (a, type(a).__name__))
                    return str.__new__(cls, *args, **kwargs)

            @unique
            class Decision1(StrEnum):
                REVERT = "REVERT"
                REVERT_ALL = "REVERT_ALL"
                RETRY = "RETRY"

            class MyEnum(StrEnum):
                pass

            @unique
            class Decision2(MyEnum):
                REVERT = "REVERT"
                REVERT_ALL = "REVERT_ALL"

    def test_empty_globals(self):
        if not six.PY2:
            # bpo-35717: sys._getframe(2).f_globals['__name__'] fails with KeyError
            # when using compile and exec because f_globals is empty
            code = "from py_enum.enum import Enum; Enum('Animal', 'ANT BEE CAT DOG')"
            code = compile(code, "<string>", "exec")
            global_ns = {}
            local_ls = {}
            exec(code, global_ns, local_ls)


class TestOrder(unittest.TestCase):

    def test_same_members(self):
        class Color(Enum):
            _order_ = 'red green blue'
            red = 1
            green = 2
            blue = 3

    def test_same_members_with_aliases(self):
        if not six.PY2:
            class Color(Enum):
                _order_ = 'red green blue'
                red = 1
                green = 2
                blue = 3
                verde = green

    def assertRaisesRegex(self, expected_exception, expected_regex, *args, **kwargs):
        if six.PY2:
            return self.assertRaises(expected_exception)
        return super(TestOrder, self).assertRaisesRegex(expected_exception, expected_regex, *args, **kwargs)

    def test_same_members_wrong_order(self):
        if not six.PY2:
            with self.assertRaisesRegex(TypeError, 'member order does not match _order_'):
                class Color(Enum):
                    _order_ = 'red green blue'
                    red = 1
                    blue = 3
                    green = 2

    def test_order_has_extra_members(self):
        with self.assertRaisesRegex(TypeError, 'member order does not match _order_'):
            class Color(Enum):
                _order_ = 'red green blue purple'
                red = 1
                green = 2
                blue = 3

    def test_order_has_extra_members_with_aliases(self):
        with self.assertRaisesRegex(TypeError, 'member order does not match _order_'):
            class Color(Enum):
                _order_ = 'red green blue purple'
                red = 1
                green = 2
                blue = 3
                verde = green

    def test_enum_has_extra_members(self):
        with self.assertRaisesRegex(TypeError, 'member order does not match _order_'):
            class Color(Enum):
                _order_ = 'red green blue'
                red = 1
                green = 2
                blue = 3
                purple = 4

    def test_enum_has_extra_members_with_aliases(self):
        with self.assertRaisesRegex(TypeError, 'member order does not match _order_'):
            class Color(Enum):
                _order_ = 'red green blue'
                red = 1
                green = 2
                blue = 3
                purple = 4
                verde = green


class TestEmptyAndNonLatinStrings(unittest.TestCase):

    def test_empty_string(self):
        with self.assertRaises(ValueError):
            Enum('empty_abc', ('', 'B', 'C'))

    def test_non_latin_character_string(self):
        greek_abc = Enum('greek_abc', ('\u03B1', 'B', 'C'))
        item = getattr(greek_abc, '\u03B1')
        self.assertEqual(item.value, 1)

    def test_non_latin_number_string(self):
        hebrew_123 = Enum('hebrew_123', ('\u05D0', '2', '3'))
        item = getattr(hebrew_123, '\u05D0')
        self.assertEqual(item.value, 1)


class TestUnique(unittest.TestCase):

    def test_unique_clean(self):
        @unique
        class Clean(Enum):
            one = 1
            two = 'dos'
            tres = 4.0

    def test_unique_dirty(self):
        if not six.PY2:
            with self.assertRaisesRegex(ValueError, 'tres.*one'):
                @unique
                class Dirty(Enum):
                    one = 1
                    two = 'dos'
                    tres = 1
        else:
            with self.assertRaises(ValueError):
                @unique
                class Dirty(Enum):
                    one = 1
                    two = 'dos'
                    tres = 1

    def test_unique_with_name(self):
        @unique
        class Silly(Enum):
            one = 1
            two = 'dos'
            name = 3


class TestStdLib(unittest.TestCase):
    maxDiff = None

    class Color(Enum):
        red = 1
        green = 2
        blue = 3

    def test_inspect_getmembers(self):
        values = dict((
            ('__class__', EnumMeta),
            ('__doc__', 'An enumeration.'),
            ('__members__', self.Color.__members__),
            ('__module__', __name__),
            ('blue', self.Color.blue),
            ('green', self.Color.green),
            ('red', self.Color.red),
        ))
        result = dict(inspect.getmembers(self.Color))
        self.assertEqual(values.keys(), result.keys())
        failed = False
        for k in values.keys():
            if result[k] != values[k]:
                print()
                print('\n%s\n     key: %s\n  result: %s\nexpected: %s\n%s\n' %
                      ('=' * 75, k, result[k], values[k], '=' * 75))
                failed = True
        if failed:
            self.fail("result does not equal expected, see print above")

    def test_inspect_classify_class_attrs(self):
        # indirectly test __objclass__
        from inspect import Attribute
        values = [
            Attribute(name='__class__', kind='data', defining_class=object, object=EnumMeta),
            Attribute(name='__doc__', kind='data', defining_class=self.Color, object='An enumeration.'),
            Attribute(name='__members__', kind='property', defining_class=EnumMeta, object=EnumMeta.__members__),
            Attribute(name='__module__', kind='data', defining_class=self.Color, object=__name__),
            Attribute(name='blue', kind='data', defining_class=self.Color, object=self.Color.blue),
            Attribute(name='green', kind='data', defining_class=self.Color, object=self.Color.green),
            Attribute(name='red', kind='data', defining_class=self.Color, object=self.Color.red),
        ]
        values.sort(key=lambda item: item.name)
        result = list(inspect.classify_class_attrs(self.Color))
        result.sort(key=lambda item: item.name)
        failed = False
        for v, r in zip(values, result):
            if r != v:
                if six.PY2 and v.name in ['__class__', '__members__']:
                    continue
                print('\n%s\n%s\n%s\n%s\n' % ('=' * 75, r, v, '=' * 75))
                failed = True
        if failed:
            self.fail("result does not equal expected, see print above")


class MiscTestCase(unittest.TestCase):
    def test__all__(self):
        if not six.PY2:
            support.check__all__(self, enum)


if __name__ == '__main__':
    unittest.main()
