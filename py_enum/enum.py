#!/usr/bin/env python
# coding=utf-8
"""
代码源于python3源码，删除了enum部功能；
增加了python2的支持；
"""
from __future__ import print_function

import copy

import six
import sys

from collections import OrderedDict
from .utils import DynamicClassAttribute


__all__ = ['EnumMeta', 'Enum', 'unique']


def _is_descriptor(obj):
    """Returns True if obj is a descriptor, False otherwise."""
    return hasattr(obj, '__get__') or hasattr(obj, '__set__') or hasattr(obj, '__delete__')


def _is_dunder(name):
    """Returns True if a __dunder__ name, False otherwise."""
    return len(name) > 4 and name[:2] == name[-2:] == '__' and name[2] != '_' and name[-3] != '_'


def _is_sunder(name):
    """Returns True if a _sunder_ name, False otherwise."""
    return len(name) > 2 and name[0] == name[-1] == '_' and name[1:2] != '_' and name[-2:-1] != '_'


def _make_class_unpicklable(cls):
    """Make the given class un-picklable."""
    def _break_on_call_reduce(self, proto):
        raise TypeError('%r cannot be pickled' % self)
    cls.__reduce_ex__ = _break_on_call_reduce
    cls.__module__ = '<unknown>'


class _EnumDict(dict):
    """Track enum member order and ensure member names are not reused.

    EnumMeta will use the names found in self._member_names as the
    enumeration member names.

    """
    def __init__(self):
        super(_EnumDict, self).__init__()
        self._member_names = []
        self._ignore = []

    def __setitem__(self, key, value):
        """Changes anything not dundered or not a descriptor.

        If an enum member name is used twice, an error is raised; duplicate
        values are not checked for.

        Single underscore (sunder) names are reserved.

        """
        if _is_sunder(key):
            if key not in ('_order_', '_create_pseudo_member_', '_ignore_', '_missing_', '_generate_next_value_'):
                raise ValueError('_names_ are reserved for future Enum use')
            if key == '_ignore_':
                if isinstance(value, str):
                    value = value.replace(',', ' ').split()
                else:
                    value = list(value)
                self._ignore = value
                already = set(value) & set(self._member_names)
                if already:
                    raise ValueError('_ignore_ cannot specify already set names: %r' % (already, ))
        elif _is_dunder(key):
            if key == '__order__':
                key = '_order_'
        elif key in self._member_names:
            # descriptor overwriting an enum?
            raise TypeError('Attempted to reuse key: %r' % key)
        elif key in self._ignore:
            pass
        elif not _is_descriptor(value):
            if key in self:
                # enum overwriting a descriptor?
                raise TypeError('%r already defined as: %r' % (key, self[key]))
            self._member_names.append(key)
        super(_EnumDict, self).__setitem__(key, value)

    @classmethod
    def py2_init(cls, fields):
        self = cls()
        for key, value in six.iteritems(fields):
            self[key] = value
        return self


# Dummy value for Enum as EnumMeta explicitly checks for it, but of course
# until EnumMeta finishes running the first time the Enum class doesn't exist.
# This is also why there are checks in EnumMeta like `if Enum is not None`
Enum = None


class EnumMeta(type):
    """Metaclass for Enum"""
    @classmethod
    def __prepare__(metacls, cls, bases):
        # create the namespace dict
        enum_dict = _EnumDict()
        return enum_dict

    def __new__(metacls, cls, bases, classdict):
        # an Enum class is final once enumeration items have been defined; it
        # cannot be mixed with other types (int, float, etc.) if it has an
        # inherited __new__ unless a new __new__ is defined (or the resulting
        # class will fail).

        if six.PY2:
            # python2没有__prepare__，所以需要单独初始化
            classdict = _EnumDict.py2_init(classdict)

        # remove any keys listed in _ignore_
        classdict.setdefault('_ignore_', []).append('_ignore_')
        ignore = classdict['_ignore_']
        for key in ignore:
            classdict.pop(key, None)
        member_type, first_enum = metacls._get_mixins_(bases)
        __new__, save_new, use_args = metacls._find_new_(classdict, member_type, first_enum)

        # save enum items into separate mapping so they don't get baked into
        # the new class
        enum_members = {k: classdict[k] for k in classdict._member_names}
        for name in classdict._member_names:
            del classdict[name]

        # adjust the sunders
        _order_ = classdict.pop('_order_', None)

        # check for illegal enum names (any others?)
        invalid_names = set(enum_members) & {'mro', ''}
        if invalid_names:
            raise ValueError('Invalid enum member name: {0}'.format(
                ','.join(invalid_names)))

        # create a default docstring if one has not been provided
        if '__doc__' not in classdict:
            classdict['__doc__'] = 'An enumeration.'

        # 为了兼容 Python2 从后面挪到了前面
        # replace any other __new__ with our own (as long as Enum is not None,
        # anyway) -- again, this is to support pickle
        if Enum is not None:
            # if the user defined their own __new__, save it before it gets
            # clobbered in case they subclass later
            if save_new:
                classdict['__new_member__'] = __new__
            classdict['__new__'] = Enum.__new__

        # create our new Enum type
        enum_class = super(EnumMeta, metacls).__new__(metacls, cls, bases, classdict)
        enum_class._member_names_ = []               # names in definition order
        enum_class._member_map_ = OrderedDict()      # name->value map
        enum_class._member_type_ = member_type

        # save DynamicClassAttribute attributes from super classes so we know
        # if we can take the shortcut of storing members in the class dict
        dynamic_attributes = {
            k for c in enum_class.mro()
            for k, v in c.__dict__.items()
            if isinstance(v, DynamicClassAttribute)
        }

        # Reverse value->name map for hashable values.
        enum_class._value2member_map_ = {}

        # If a custom type is mixed into the Enum, and it does not know how
        # to pickle itself, pickle.dumps will succeed but pickle.loads will
        # fail.  Rather than have the error show up later and possibly far
        # from the source, sabotage the pickle protocol for this class so
        # that pickle.dumps also fails.
        #
        # However, if the new class implements its own __reduce_ex__, do not
        # sabotage -- it's on them to make sure it works correctly.  We use
        # __reduce_ex__ instead of any of the others as it is preferred by
        # pickle over __reduce__, and it handles all pickle protocols.
        if '__reduce_ex__' not in classdict:
            if member_type is not object:
                methods = ('__getnewargs_ex__', '__getnewargs__', '__reduce_ex__', '__reduce__')
                if not any(m in member_type.__dict__ for m in methods):
                    _make_class_unpicklable(enum_class)

        # instantiate them, checking for duplicates as we go
        # we instantiate first instead of checking for duplicates first in case
        # a custom __new__ is doing something funky with the values -- such as
        # auto-numbering ;)
        for member_name, value in six.iteritems(enum_members):
            if not isinstance(value, tuple):
                args = (value, )
            else:
                args = value
            if member_type is tuple:   # special case for tuple enums
                args = (args, )     # wrap it one more time
            if not use_args:
                enum_member = __new__(enum_class)
                if not hasattr(enum_member, '_value_'):
                    enum_member._value_ = value
            else:
                enum_member = __new__(enum_class, *args)
                if not hasattr(enum_member, '_value_'):
                    if member_type is object:
                        enum_member._value_ = value
                    else:
                        enum_member._value_ = member_type(*args)
            value = enum_member._value_
            enum_member._name_ = member_name
            enum_member.__objclass__ = enum_class

            enum_member.__init__(*args)
            # If another member with the same value was already defined, the
            # new member becomes an alias to the existing one.
            for name, canonical_member in six.iteritems(enum_class._member_map_):
                if canonical_member._value_ == enum_member._value_:
                    enum_member = canonical_member
                    break
            else:
                # Aliases don't appear in member names (only in __members__).
                enum_class._member_names_.append(member_name)

            # performance boost for any member that would not shadow
            # a DynamicClassAttribute
            if member_name not in dynamic_attributes:
                setattr(enum_class, member_name, enum_member)

            # now add to _member_map_
            enum_class._member_map_[member_name] = enum_member
            try:
                # This may fail if value is not hashable. We can't add the value
                # to the map, and by-value lookups for this value will be
                # linear.
                enum_class._value2member_map_[value] = enum_member
            except TypeError:
                pass

        # double check that repr and friends are not the mixin's or various
        # things break (such as pickle)
        for name in ('__repr__', '__str__', '__format__', '__reduce_ex__'):
            class_method = getattr(enum_class, name)
            obj_method = getattr(member_type, name, None)
            enum_method = getattr(first_enum, name, None)
            if obj_method is not None and obj_method is class_method:
                setattr(enum_class, name, enum_method)

        # py3 support for definition order (helps keep py2/py3 code in sync)
        if _order_ is not None:
            if isinstance(_order_, str):
                _order_ = _order_.replace(',', ' ').split()
            if six.PY2:
                if sorted(_order_) != sorted(enum_class._member_names_):
                    raise TypeError('member order does not match _order_')
                # python2直接使用_order_实现排序
                enum_class._member_names_ = copy.deepcopy(_order_)
            else:
                if _order_ != enum_class._member_names_:
                    raise TypeError('member order does not match _order_')

        return enum_class

    def __call__(cls, value, names=None, module=None, qualname=None, type=None, start=1, **kwargs):
        """Either returns an existing member, or creates a new enum class.

        This method is used both when an enum class is given a value to match
        to an enumeration member (i.e. Color(3)) and for the functional API
        (i.e. Color = Enum('Color', names='RED GREEN BLUE')).

        When used for the functional API:

        `value` will be the name of the new class.

        `names` should be either a string of white-space/comma delimited names
        (values will start at `start`), or an iterator/mapping of name, value pairs.

        `module` should be set to the module this class is being created in;
        if it is not set, an attempt to find that module will be made, but if
        it fails the class will not be picklable.

        `qualname` should be set to the actual location this class can be found
        at in its module; by default it is set to the global scope.  If this is
        not correct, unpickling will fail in some circumstances.

        `type`, if set, will be mixed in as the first base class.

        """
        if names is None:  # simple value lookup
            return cls.__new__(cls, value)
        # otherwise, functional API: we're creating a new Enum type
        return cls._create_(value, names, module=module, qualname=qualname, type=type, start=start, **kwargs)

    def __bool__(self):
        """
        classes/types should always be True.
        """
        return True

    def __contains__(cls, member):
        if not isinstance(member, Enum):
            import warnings
            warnings.warn(
                    "using non-Enums in containment checks will raise "
                    "TypeError in Python 3.8",
                    DeprecationWarning, 2)
        return isinstance(member, cls) and member._name_ in cls._member_map_

    def __delattr__(cls, attr):
        # nicer error message when someone tries to delete an attribute
        # (see issue19025).
        if attr in cls._member_map_:
            raise AttributeError("%s: cannot delete Enum member." % cls.__name__)
        super(EnumMeta, cls).__delattr__(attr)

    def __dir__(self):
        return ['__class__', '__doc__', '__members__', '__module__'] + self._member_names_

    def __getattr__(cls, name):
        """Return the enum member matching `name`

        We use __getattr__ instead of descriptors or inserting into the enum
        class' __dict__ in order to support `name` and `value` being both
        properties for enum members (which live in the class' __dict__) and
        enum members themselves.

        """
        if _is_dunder(name):
            raise AttributeError(name)
        try:
            return cls._member_map_[name]
        except KeyError:
            six.raise_from(AttributeError(name), None)

    def __getitem__(cls, name):
        return cls._member_map_[name]

    def __iter__(cls):
        return (cls._member_map_[name] for name in cls._member_names_)

    def __len__(cls):
        return len(cls._member_names_)

    @property
    def __members__(cls):
        """Returns a mapping of member name->value.

        This mapping lists all enum members, including aliases. Note that this
        is a read-only view of the internal mapping.

        """
        return cls._member_map_.copy()

    def __repr__(cls):
        return "<enum %r>" % cls.__name__

    def __reversed__(cls):
        return (cls._member_map_[name] for name in reversed(cls._member_names_))

    def __setattr__(cls, name, value):
        """Block attempts to reassign Enum members.

        A simple assignment to the class namespace only changes one of the
        several possible ways to get an Enum member from the Enum class,
        resulting in an inconsistent Enumeration.

        """
        member_map = cls.__dict__.get('_member_map_', {})
        if name in member_map:
            raise AttributeError('Cannot reassign members.')
        super(EnumMeta, cls).__setattr__(name, value)

    def _create_(cls, class_name, names, module=None, qualname=None, type=None, start=1, **kwargs):
        """Convenience method to create a new Enum class.

        `names` can be:

        * A string containing member names, separated either with spaces or
          commas.  Values are incremented by 1 from `start`.
        * An iterable of member names.  Values are incremented by 1 from `start`.
        * An iterable of (member name, value) pairs.
        * A mapping of member name -> value pairs.

        """
        metacls = cls.__class__
        bases = (cls, ) if type is None else (type, cls)
        _, first_enum = cls._get_mixins_(bases)
        classdict = metacls.__prepare__(class_name, bases)

        # special processing needed for names?
        if isinstance(names, str):
            names = names.replace(',', ' ').split()
        if isinstance(names, (tuple, list)) and names and isinstance(names[0], str):
            original_names, names = names, []
            last_values = []
            for count, name in enumerate(original_names):
                value = first_enum._generate_next_value_(name, start, count, last_values[:])
                last_values.append(value)
                names.append((name, value))

        # Here, names is either an iterable of (name, value) or a mapping.
        for item in names:
            if isinstance(item, str):
                member_name, member_value = item, names[item]
            else:
                member_name, member_value = item
            classdict[member_name] = member_value
        enum_class = metacls.__new__(metacls, class_name, bases, classdict)

        # TODO: replace the frame hack if a blessed way to know the calling
        # module is ever developed
        if module is None:
            try:
                module = sys._getframe(2).f_globals['__name__']
            except (AttributeError, ValueError, KeyError):
                pass
        if module is None:
            _make_class_unpicklable(enum_class)
        else:
            enum_class.__module__ = module
        if qualname is not None:
            enum_class.__qualname__ = qualname

        return enum_class

    @staticmethod
    def _get_mixins_(bases):
        """Returns the type for creating enum members, and the first inherited
        enum class.

        bases: the tuple of bases that was given to __new__

        """
        if not bases:
            return object, Enum

        def _find_data_type(bases):
            for chain in bases:
                for base in chain.__mro__:
                    if base is object:
                        continue
                    elif '__new__' in base.__dict__:
                        if issubclass(base, Enum):
                            continue
                        return base

        # ensure final parent class is an Enum derivative, find any concrete
        # data type, and check that Enum has no members
        first_enum = bases[-1]
        if not issubclass(first_enum, Enum):
            raise TypeError(
                "new enumerations should be created as `EnumName([mixin_type, ...] [data_type,] enum_type)`"
            )
        member_type = _find_data_type(bases) or object
        if first_enum._member_names_:
            raise TypeError("Cannot extend enumerations")
        return member_type, first_enum

    @staticmethod
    def _find_new_(classdict, member_type, first_enum):
        """Returns the __new__ to be used for creating the enum members.

        classdict: the class dictionary given to __new__
        member_type: the data type whose __new__ will be used by default
        first_enum: enumeration to check for an overriding __new__

        """
        # now find the correct __new__, checking to see of one was defined
        # by the user; also check earlier enum classes in case a __new__ was
        # saved as __new_member__
        __new__ = classdict.get('__new__', None)

        # should __new__ be saved as __new_member__ later?
        save_new = __new__ is not None

        if __new__ is None:
            # check all possibles for __new_member__ before falling back to
            # __new__
            for method in ('__new_member__', '__new__'):
                for possible in (member_type, first_enum):
                    target = getattr(possible, method, None)
                    if target not in (None, None.__new__, object.__new__, Enum.__new__):
                        __new__ = target
                        break
                if __new__ is not None:
                    break
            else:
                __new__ = object.__new__

        # if a non-object.__new__ is used then whatever value/tuple was
        # assigned to the enum member name will be passed to __new__ and to the
        # new enum member's __init__
        if __new__ is object.__new__:
            use_args = False
        else:
            use_args = True
        return __new__, save_new, use_args


class Enum(six.with_metaclass(EnumMeta)):
    """Generic enumeration.
    Derive from this class to define new enumerations.
    """
    def __new__(cls, value):
        # all enum instances are actually created during class construction
        # without calling this method; this method is called by the metaclass'
        # __call__ (i.e. Color(3) ), and by pickle
        if type(value) is cls:
            # For lookups like Color(Color.RED)
            return value
        # by-value search for a matching enum member
        # see if it's in the reverse mapping (for hashable values)
        try:
            return cls._value2member_map_[value]
        except KeyError:
            # Not found, no need to do long O(n) search
            pass
        except TypeError:
            # not there, now do long search -- O(n) behavior
            for member in cls._member_map_.values():
                if member._value_ == value:
                    return member

        # still not found -- try _missing_ hook
        try:
            exc = None
            result = cls._missing_(value)
        except Exception as e:
            exc = e
            result = None
        if isinstance(result, cls):
            return result
        else:
            ve_exc = ValueError("%r is not a valid %s" % (value, cls.__name__))
            if result is None and exc is None:
                raise ve_exc
            elif exc is None:
                exc = TypeError(
                        'error in %s._missing_: returned %r instead of None or a valid member'
                        % (cls.__name__, result)
                        )
            exc.__context__ = ve_exc
            raise exc

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        for last_value in reversed(last_values):
            try:
                return last_value + 1
            except TypeError:
                pass
        else:
            return start

    @classmethod
    def _missing_(cls, value):
        raise ValueError("%r is not a valid %s" % (value, cls.__name__))

    def __repr__(self):
        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, self._value_)

    def __str__(self):
        return "%s.%s" % (self.__class__.__name__, self._name_)

    def __dir__(self):
        added_behavior = [
            m
            for cls in self.__class__.mro()
            for m in cls.__dict__
            if m[0] != '_' and m not in self._member_map_
        ]
        return ['__class__', '__doc__', '__module__'] + added_behavior

    def __format__(self, format_spec):
        # mixed-in Enums should use the mixed-in type's __format__, otherwise
        # we can get strange results with the Enum name showing up instead of
        # the value

        # pure Enum branch
        if self._member_type_ is object:
            cls = str
            val = str(self)
        # mix-in branch
        else:
            cls = self._member_type_
            val = self._value_
        return cls.__format__(val, format_spec)

    def __hash__(self):
        return hash(self._name_)

    def __reduce_ex__(self, proto):
        return self.__class__, (self._value_, )

    @DynamicClassAttribute
    def name(self):
        """The name of the Enum member."""
        return self._name_

    @DynamicClassAttribute
    def value(self):
        """The value of the Enum member."""
        return self._value_


def unique(enumeration):
    """Class decorator for enumerations ensuring unique member values."""
    duplicates = []
    for name, member in six.iteritems(enumeration.__members__):
        if name != member.name:
            duplicates.append((name, member.name))
    if duplicates:
        alias_details = ', '.join(["%s -> %s" % (alias, name) for (alias, name) in duplicates])
        raise ValueError('duplicate values found in %r: %s' % (enumeration, alias_details))
    return enumeration
