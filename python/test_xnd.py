#
# BSD 3-Clause License
#
# Copyright (c) 2017, plures
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import sys, unittest
from math import isinf, isnan
from ndtypes import ndt
from xnd import xnd
from support import *
from randvalue import *


# NumPy tests disabled: importing numpy causes memory leaks in Python3.
np = None


SKIP_LONG = True
SKIP_BRUTE_FORCE = True

if '--long' in sys.argv:
    SKIP_LONG = False
    sys.argv.remove('--long')
if '--all' in sys.argv:
    SKIP_LONG = False
    SKIP_BRUTE_FORCE = False
    sys.argv.remove('--all')


PRIMITIVE = [
    'bool',
    'int8', 'int16', 'int32', 'int64',
    'uint8', 'uint16', 'uint32', 'uint64',
    'float32', 'float64',
    'complex64', 'complex128'
]

EMPTY_TEST_CASES = [
    (0, "%s"),
    ([], "0 * %s"),
    ([0], "1 * %s"),
    ([0, 0], "var(offsets=[0, 2]) * %s"),
    (3 * [{"a": 0, "b": 0}], "3 * {a: int64, b: %s}")
]


class TestFixedDim(unittest.TestCase):

    def test_fixed_dim_empty(self):
        for v, s in DTYPE_EMPTY_TEST_CASES:
            for vv, ss in [
               (0 * [v], "0 * %s" % s),
               (1 * [v], "1 * %s" % s),
               (2 * [v], "2 * %s" % s),
               (1000 * [v], "1000 * %s" % s),

               (0 * [0 * [v]], "0 * 0 * %s" % s),
               (0 * [1 * [v]], "0 * 1 * %s" % s),
               (1 * [0 * [v]], "1 * 0 * %s" % s),

               (1 * [1 * [v]], "1 * 1 * %s" % s),
               (1 * [2 * [v]], "1 * 2 * %s" % s),
               (2 * [1 * [v]], "2 * 1 * %s" % s),
               (2 * [2 * [v]], "2 * 2 * %s" % s),
               (2 * [3 * [v]], "2 * 3 * %s" % s),
               (3 * [2 * [v]], "3 * 2 * %s" % s),
               (3 * [40 * [v]], "3 * 40 * %s" % s) ]:

                t = ndt(ss)
                x = xnd.empty(ss)
                self.assertEqual(x.type, t)
                self.assertEqual(x.value, vv)


class TestVarDim(unittest.TestCase):

    def test_var_dim_empty(self):
        for v, s in DTYPE_EMPTY_TEST_CASES:
            for vv, ss in [
               (0 * [v], "var(offsets=[0,0]) * %s" % s),
               (1 * [v], "var(offsets=[0,1]) * %s" % s),
               (2 * [v], "var(offsets=[0,2]) * %s" % s),
               (1000 * [v], "var(offsets=[0,1000]) * %s" % s),

               (1 * [0 * [v]], "var(offsets=[0,1]) * var(offsets=[0,0]) * %s" % s),

               ([[v], []], "var(offsets=[0,2]) * var(offsets=[0,1,1]) * %s" % s),
               ([[], [v]], "var(offsets=[0,2]) * var(offsets=[0,0,1]) * %s" % s),

               ([[v], [v]], "var(offsets=[0,2]) * var(offsets=[0,1,2]) * %s" % s),
               ([[v], 2 * [v], 5 * [v]], "var(offsets=[0,3]) * var(offsets=[0,1,3,8]) * %s" % s)]:

                t = ndt(ss)
                x = xnd.empty(ss)
                self.assertEqual(x.type, t)
                self.assertEqual(x.value, vv)


class TestSymbolicDim(unittest.TestCase):

    def test_symbolic_dim_raise(self):
        for _, s in DTYPE_EMPTY_TEST_CASES:
            for err, ss in [
               (ValueError, "N * %s" % s),
               (ValueError, "10 * N * %s" % s),
               (ValueError, "N * 10 * N * %s" % s),
               (ValueError, "X * 10 * N * %s" % s)]:

                t = ndt(ss)
                self.assertRaises(err, xnd.empty, t)


class TestEllipsisDim(unittest.TestCase):

    def test_ellipsis_dim_raise(self):
        for _, s in DTYPE_EMPTY_TEST_CASES:
            for err, ss in [
               (ValueError, "... * %s" % s),
               (ValueError, "Dims... * %s" % s),
               (ValueError, "... * 10 * %s" % s),
               (ValueError, "10 * ... * 10 * %s" % s),
               (ValueError, "10 * A... * 10 * %s" % s),
               (ValueError, "10 * 10 * B... * ref(%s)" % s),
               (ValueError, "10 * A... * 10 * Some(ref(%s))" % s),
               (ValueError, "10 * 10 * B... * Some(ref(ref(%s)))" % s)]:

                t = ndt(ss)
                self.assertRaises(err, xnd.empty, t)


class TestTuple(unittest.TestCase):

    def test_tuple_empty(self):
        for v, s in DTYPE_EMPTY_TEST_CASES:
            for vv, ss in [
               ((v,), "(%s)" % s),
               (((v,),), "((%s))" % s),
               ((((v,),),), "(((%s)))" % s),

               ((0 * [v],), "(0 * %s)" % s),
               (((0 * [v],),), "((0 * %s))" % s),
               ((1 * [v],), "(1 * %s)" % s),
               (((1 * [v],),), "((1 * %s))" % s),
               ((3 * [v],), "(3 * %s)" % s),
               (((3 * [v],),), "((3 * %s))" % s)]:

                t = ndt(ss)
                x = xnd.empty(ss)
                self.assertEqual(x.type, t)
                self.assertEqual(x.value, vv)


class TestRecord(unittest.TestCase):

    def test_record_empty(self):
        for v, s in DTYPE_EMPTY_TEST_CASES:
            for vv, ss in [
               ({'x': v}, "{x: %s}" % s),
               ({'x': {'y': v}}, "{x: {y: %s}}" % s),

               ({'x': 0 * [v]}, "{x: 0 * %s}" % s),
               ({'x': {'y': 0 * [v]}}, "{x: {y: 0 * %s}}" % s),
               ({'x': 1 * [v]}, "{x: 1 * %s}" % s),
               ({'x': 3 * [v]}, "{x: 3 * %s}" % s)]:

                t = ndt(ss)
                x = xnd.empty(ss)
                self.assertEqual(x.type, t)
                self.assertEqual(x.value, vv)


class TestRef(unittest.TestCase):

    def test_ref_empty(self):
        for v, s in DTYPE_EMPTY_TEST_CASES:
            for vv, ss in [
               (v, "ref(%s)" % s),
               (v, "ref(ref(%s))" % s),
               (v, "ref(ref(ref(%s)))" % s),

               (0 * [v], "ref(0 * %s)" % s),
               (0 * [v], "ref(ref(0 * %s))" % s),
               (0 * [v], "ref(ref(ref(0 * %s)))" % s),
               (1 * [v], "ref(1 * %s)" % s),
               (1 * [v], "ref(ref(1 * %s))" % s),
               (1 * [v], "ref(ref(ref(1 * %s)))" % s),
               (3 * [v], "ref(3 * %s)" % s),
               (3 * [v], "ref(ref(3 * %s))" % s),
               (3 * [v], "ref(ref(ref(3 * %s)))" % s)]:

                t = ndt(ss)
                x = xnd.empty(ss)
                self.assertEqual(x.type, t)
                self.assertEqual(x.value, vv)


class TestConstr(unittest.TestCase):

    def test_constr_empty(self):
        for v, s in DTYPE_EMPTY_TEST_CASES:
            for vv, ss in [
               (v, "SomeConstr(%s)" % s),
               (v, "Just(Some(%s))" % s),

               (0 * [v], "Some(0 * %s)" % s),
               (1 * [v], "Some(1 * %s)" % s),
               (3 * [v], "Maybe(3 * %s)" % s)]:

                t = ndt(ss)
                x = xnd.empty(ss)
                self.assertEqual(x.type, t)
                self.assertEqual(x.value, vv)


class TestCategorical(unittest.TestCase):

    def test_categorical_empty(self):
        # Categorical values are stored as indices into the type's categories.
        # Since empty xnd objects are initialized to zero, the value of an
        # empty categorical entry is always the value of the first category.
        # This is safe, since categorical types must have at least one entry.
        r = R['a': "", 'b': 1.2]
        rt = "{a: string, b: categorical(1.2, 10.0, NA)}"

        test_cases = [
          ("January", "categorical('January')"),
          ((None,), "(categorical(NA, 'January', 'August'))"),
          (10 * [2 * [1.2]], "10 * 2 * categorical(1.2, 10.0, NA)"),
          (10 * [2 * [100]], "10 * 2 * categorical(100, 'mixed')"),
          (10 * [2 * [r]], "10 * 2 * %s" % rt),
          ([2 * [r], 5 * [r], 3 * [r]], "var(offsets=[0,3]) * var(offsets=[0,2,7,10]) * %s" % rt)
        ]

        for v, s in test_cases:
            t = ndt(s)
            x = xnd.empty(s)
            self.assertEqual(x.type, t)
            self.assertEqual(x.value, v)


class TestFixedString(unittest.TestCase):

    def test_fixed_string_empty(self):
        test_cases = [
          ('fixed_string(1)', '\x00'),
          ('fixed_string(3)', 3 * '\x00'),
          ("fixed_string(1, 'ascii')", '\x00'),
          ("fixed_string(3, 'utf8')", 3 * '\x00'),
          ("fixed_string(3, 'utf16')", 3 * '\x00'),
          ("fixed_string(3, 'utf32')", 3 * '\x00'),
          ("2 * fixed_string(3, 'utf32')", 2 * [3 * '\x00']),
        ]

        for s, v in test_cases:
            t = ndt(s)
            x = xnd.empty(s)
            self.assertEqual(x.type, t)
            self.assertEqual(x.value, v)

    def test_fixed_string(self):
        t = "2 * fixed_string(3, 'utf16')"
        v = ["\u1111\u2222\u3333", "\u1112\u2223\u3334"]
        x = xnd(v, type=t)
        self.assertEqual(x.value, v)


        t = "2 * fixed_string(3, 'utf32')"
        v = ["\U00011111\U00022222\U00033333", "\U00011112\U00022223\U00033334"]
        x = xnd(v, type=t)
        self.assertEqual(x.value, v)


class TestString(unittest.TestCase):

    def test_string_empty(self):
        test_cases = [
          'string',
          '(string)',
          '10 * 2 * string',
          '10 * 2 * (string, string)',
          '10 * 2 * {a: string, b: string}',
          'var(offsets=[0,3]) * var(offsets=[0,2,7,10]) * {a: string, b: string}'
        ]

        for s in test_cases:
            t = ndt(s)
            x = xnd.empty(s)
            self.assertEqual(x.type, t)

        t = ndt('string')
        x = xnd.empty(t)
        self.assertEqual(x.type, t)
        self.assertEqual(x.value, '')

        t = ndt('10 * string')
        x = xnd.empty(t)
        self.assertEqual(x.type, t)
        for i in range(10):
            self.assertEqual(x[i], '')

    def test_string(self):
        t = '2 * {a: complex128, b: string}'
        x = xnd([R['a': 2+3j, 'b': "thisguy"], R['a': 1+4j, 'b': "thatguy"]], type=t)

        self.assertEqual(x[0]['b'], "thisguy")
        self.assertEqual(x[1]['b'], "thatguy")


class TestBytes(unittest.TestCase):

    def test_bytes_empty(self):
        r = R['a': b'', 'b': b'']

        test_cases = [
          (b'', 'bytes(align=16)'),
          ((b'',), '(bytes(align=32))'),
          (3 * [2 * [b'']], '3 * 2 * bytes'),
          (10 * [2 * [(b'', b'')]], '10 * 2 * (bytes, bytes)'),
          (10 * [2 * [r]], '10 * 2 * {a: bytes(align=32), b: bytes(align=1)}'),
          (10 * [2 * [r]], '10 * 2 * {a: bytes(align=1), b: bytes(align=32)}'),
          ([2 * [r], 5 * [r], 3 * [r]], 'var(offsets=[0,3]) * var(offsets=[0,2,7,10]) * {a: bytes(align=32), b: bytes}')
        ]

        for v, s in test_cases:
            t = ndt(s)
            x = xnd.empty(s)
            self.assertEqual(x.type, t)
            self.assertEqual(x.value, v)


class TestFixedBytes(unittest.TestCase):

    def test_fixed_bytes_empty(self):
        r = R['a': 3 * b'\x00', 'b': 10 * b'\x00']

        test_cases = [
          (b'\x00', 'fixed_bytes(size=1)'),
          (100 * b'\x00', 'fixed_bytes(size=100)'),
          (b'\x00', 'fixed_bytes(size=1, align=2)'),
          (100 * b'\x00', 'fixed_bytes(size=100, align=16)'),
          (r, '{a: fixed_bytes(size=3), b: fixed_bytes(size=10)}'),
          (2 * [3 * [r]], '2 * 3 * {a: fixed_bytes(size=3), b: fixed_bytes(size=10)}')
        ]

        for v, s in test_cases:
            t = ndt(s)
            x = xnd.empty(s)
            self.assertEqual(x.type, t)
            self.assertEqual(x.value, v)


class TestPrimitive(unittest.TestCase):

    def test_primitive_empty(self):
        # Test creation and initialization of empty xnd objects.

        for value, type_string in EMPTY_TEST_CASES:
            for p in PRIMITIVE:
                ts = type_string % p
                x = xnd.empty(ts)
                self.assertEqual(x.value, value)
                self.assertEqual(x.type, ndt(ts))

    def test_bool(self):
        # From bool.
        x = xnd(True, type="bool")
        self.assertIs(x.value, True)

        x = xnd(False, type="bool")
        self.assertIs(x.value, False)

        # From int.
        x = xnd(1, type="bool")
        self.assertIs(x.value, True)

        x = xnd(0, type="bool")
        self.assertIs(x.value, False)

        # Test broken input.
        b = BoolMemoryError()
        self.assertRaises(MemoryError, xnd, b, type="bool")

    def test_signed(self):
        # Test bounds.
        for n in (8, 16, 32, 64):
            t = "int%d" % n

            v = -2**(n-1)
            x = xnd(v, type=t)
            self.assertEqual(x.value, v)
            self.assertRaises((ValueError, OverflowError), xnd, v-1, type=t)

            v = 2**(n-1) - 1
            x = xnd(v, type=t)
            self.assertEqual(x.value, v)
            self.assertRaises((ValueError, OverflowError), xnd, v+1, type=t)

        # Test index.
        i = Index()
        for n in (8, 16, 32, 64):
            t = "int%d" % n
            x = xnd(i, type=t)
            self.assertEqual(x.value, 10)

        # Test broken input.
        for n in (8, 16, 32, 64):
            t = "int%d" % n
            i = IndexMemoryError()
            self.assertRaises(MemoryError, xnd, i, type=t)
            i = IndexTypeError()
            self.assertRaises(TypeError, xnd, i, type=t)

    def test_unsigned(self):
        # Test bounds.
        for n in (8, 16, 32, 64):
            t = "uint%d" % n

            v = 0
            x = xnd(v, type=t)
            self.assertEqual(x.value, v)
            self.assertRaises((ValueError, OverflowError), xnd, v-1, type=t)

            v = 2**n - 1
            x = xnd(v, type=t)
            self.assertEqual(x.value, v)
            self.assertRaises((ValueError, OverflowError), xnd, v+1, type=t)

        # Test index.
        i = Index()
        for n in (8, 16, 32, 64):
            t = "uint%d" % n
            x = xnd(i, type=t)
            self.assertEqual(x.value, 10)

        # Test broken input.
        for n in (8, 16, 32, 64):
            t = "uint%d" % n
            i = IndexMemoryError()
            self.assertRaises(MemoryError, xnd, i, type=t)
            i = IndexTypeError()
            self.assertRaises(TypeError, xnd, i, type=t)

    @requires_py36
    def test_float16(self):
        fromhex = float.fromhex

        # Test creation and initialization of empty xnd objects.
        for value, type_string in EMPTY_TEST_CASES:
            ts = type_string % "float16"
            x = xnd.empty(ts)
            self.assertEqual(x.value, value)
            self.assertEqual(x.type, ndt(ts))

        # Test bounds.
        DENORM_MIN = fromhex("0x1p-24")
        LOWEST = fromhex("-0x1.ffcp+15")
        MAX = fromhex("0x1.ffcp+15")
        INF = fromhex("0x1.ffep+15")

        x = xnd(DENORM_MIN, type="float16")
        self.assertEqual(x.value, DENORM_MIN)

        x = xnd(LOWEST, type="float16")
        self.assertEqual(x.value, LOWEST)

        x = xnd(MAX, type="float16")
        self.assertEqual(x.value, MAX)

        self.assertRaises(OverflowError, xnd, INF, type="float16")
        self.assertRaises(OverflowError, xnd, -INF, type="float16")

        # Test special values.
        x = xnd(float("inf"), type="float16")
        self.assertTrue(isinf(x.value))

        x = xnd(float("nan"), type="float16")
        self.assertTrue(isnan(x.value))

    def test_float32(self):
        fromhex = float.fromhex

        # Test bounds.
        DENORM_MIN = fromhex("0x1p-149")
        LOWEST = fromhex("-0x1.fffffep+127")
        MAX = fromhex("0x1.fffffep+127")
        INF = fromhex("0x1.ffffffp+127")

        x = xnd(DENORM_MIN, type="float32")
        self.assertEqual(x.value, DENORM_MIN)

        x = xnd(LOWEST, type="float32")
        self.assertEqual(x.value, LOWEST)

        x = xnd(MAX, type="float32")
        self.assertEqual(x.value, MAX)

        self.assertRaises(OverflowError, xnd, INF, type="float32")
        self.assertRaises(OverflowError, xnd, -INF, type="float32")

        # Test special values.
        x = xnd(float("inf"), type="float32")
        self.assertTrue(isinf(x.value))

        x = xnd(float("nan"), type="float32")
        self.assertTrue(isnan(x.value))

    def test_float64(self):
        fromhex = float.fromhex

        # Test bounds.
        DENORM_MIN = fromhex("0x0.0000000000001p-1022")
        LOWEST = fromhex("-0x1.fffffffffffffp+1023")
        MAX = fromhex("0x1.fffffffffffffp+1023")

        x = xnd(DENORM_MIN, type="float64")
        self.assertEqual(x.value, DENORM_MIN)

        x = xnd(LOWEST, type="float64")
        self.assertEqual(x.value, LOWEST)

        x = xnd(MAX, type="float64")
        self.assertEqual(x.value, MAX)

        # Test special values.
        x = xnd(float("inf"), type="float64")
        self.assertTrue(isinf(x.value))

        x = xnd(float("nan"), type="float64")
        self.assertTrue(isnan(x.value))

    @requires_py36
    def test_complex32(self):
        fromhex = float.fromhex

        # Test creation and initialization of empty xnd objects.
        for value, type_string in EMPTY_TEST_CASES:
            ts = type_string % "complex32"
            x = xnd.empty(ts)
            self.assertEqual(x.value, value)
            self.assertEqual(x.type, ndt(ts))

        # Test bounds.
        DENORM_MIN = fromhex("0x1p-24")
        LOWEST = fromhex("-0x1.ffcp+15")
        MAX = fromhex("0x1.ffcp+15")
        INF = fromhex("0x1.ffep+15")

        v = complex(DENORM_MIN, DENORM_MIN)
        x = xnd(complex(DENORM_MIN, DENORM_MIN), type="complex32")
        self.assertEqual(x.value, v)

        v = complex(LOWEST, LOWEST)
        x = xnd(v, type="complex32")
        self.assertEqual(x.value, v)

        v = complex(MAX, MAX)
        x = xnd(v, type="complex32")
        self.assertEqual(x.value, v)

        v = complex(INF, INF)
        self.assertRaises(OverflowError, xnd, v, type="complex32")

        v = complex(-INF, -INF)
        self.assertRaises(OverflowError, xnd, v, type="complex32")

        # Test special values.
        x = xnd(complex("inf"), type="complex32")
        self.assertTrue(isinf(x.value.real))
        self.assertTrue(isinf(x.value.imag))

        x = xnd(complex("nan"), type="complex32")
        self.assertTrue(isnan(x.value.real))
        self.assertTrue(isnan(x.value.imag))

    def test_complex64(self):
        fromhex = float.fromhex

        # Test bounds.
        DENORM_MIN = fromhex("0x1p-149")
        LOWEST = fromhex("-0x1.fffffep+127")
        MAX = fromhex("0x1.fffffep+127")
        INF = fromhex("0x1.ffffffp+127")

        v = complex(DENORM_MIN, DENORM_MIN)
        x = xnd(DENORM_MIN, type="complex64")
        self.assertEqual(x.value, v)

        v = complex(LOWEST, LOWEST)
        x = xnd(v, type="complex64")
        self.assertEqual(x.value, v)

        v = complex(MAX, MAX)
        x = xnd(v, type="complex64")
        self.assertEqual(x.value, v)

        v = complex(INF, INF)
        self.assertRaises(OverflowError, xnd, INF, type="complex64")

        v = complex(-INF, -INF)
        self.assertRaises(OverflowError, xnd, -INF, type="complex64")

        # Test special values.
        x = xnd(complex("inf"), type="complex64")
        self.assertTrue(isinf(x.value.real))
        self.assertTrue(isinf(x.value.imag))

        x = xnd(complex("nan"), type="complex64")
        self.assertTrue(isnan(x.value.real))
        self.assertTrue(isnan(x.value.imag))

    def test_complex128(self):
        fromhex = float.fromhex

        # Test bounds.
        DENORM_MIN = fromhex("0x0.0000000000001p-1022")
        LOWEST = fromhex("-0x1.fffffffffffffp+1023")
        MAX = fromhex("0x1.fffffffffffffp+1023")

        v = complex(DENORM_MIN, DENORM_MIN)
        x = xnd(v, type="complex128")
        self.assertEqual(x.value, v)

        v = complex(LOWEST, LOWEST)
        x = xnd(v, type="complex128")
        self.assertEqual(x.value, v)

        v = complex(MAX, MAX)
        x = xnd(v, type="complex128")
        self.assertEqual(x.value, v)

        # Test special values.
        x = xnd(complex("inf"), type="complex128")
        self.assertTrue(isinf(x.value.real))
        self.assertTrue(isinf(x.value.imag))

        x = xnd(complex("nan"), type="complex128")
        self.assertTrue(isnan(x.value.real))
        self.assertTrue(isnan(x.value.imag))


class TypeInferenceTest(unittest.TestCase):

    def test_tuple(self):
        d = R['a': (2.0, b"bytes"), 'b': ("str", float('inf'))]
        typeof_d = "{a: (float64, bytes), b: (string, float64)}"

        test_cases = [
          ((), "()"),
          (((),), "(())"),
          (((), ()), "((), ())"),
          ((((),), ()), "((()), ())"),
          ((((),), ((), ())), "((()), ((), ()))"),
          ((1, 2, 3), "(int64, int64, int64)"),
          ((1.0, 2, "str"), "(float64, int64, string)"),
          ((1.0, 2, ("str", b"bytes", d)),
           "(float64, int64, (string, bytes, %s))" % typeof_d)
        ]

        for v, t in test_cases:
            x = xnd(v)
            self.assertEqual(x.type, ndt(t))
            self.assertEqual(x.value, v)

    def test_record(self):
        d = R['a': (2.0, b"bytes"), 'b': ("str", float('inf'))]
        typeof_d = "{a: (float64, bytes), b: (string, float64)}"

        test_cases = [
          ({}, "{}"),
          ({'x': {}}, "{x: {}}"),
          (R['x': {}, 'y': {}], "{x: {}, y: {}}"),
          (R['x': R['y': {}], 'z': {}], "{x: {y: {}}, z: {}}"),
          (R['x': R['y': {}], 'z': R['a': {}, 'b': {}]], "{x: {y: {}}, z: {a: {}, b: {}}}"),
          (d, typeof_d)
        ]

        for v, t in test_cases:
            x = xnd(v)
            self.assertEqual(x.type, ndt(t))
            self.assertEqual(x.value, v)

    def test_float64(self):
        d = R['a': 2.221e100, 'b': float('inf')]
        typeof_d = "{a: float64, b: float64}"

        test_cases = [
          # 'float64' is the default dtype if there is no data at all.
          ([], "0 * float64"),
          ([[]], "1 * 0 * float64"),
          ([[], []], "2 * 0 * float64"),
          ([[[]], [[]]], "2 * 1 * 0 * float64"),
          ([[[]], [[], []]], "var(offsets=[0, 2]) * var(offsets=[0, 1, 3]) * var(offsets=[0, 0, 0, 0]) * float64"),

          ([0.0], "1 * float64"),
          ([0.0, 1.2], "2 * float64"),
          ([[0.0], [1.2]], "2 * 1 * float64"),

          (d, typeof_d),
          ([d] * 2, "2 * %s" % typeof_d),
          ([[d] * 2] * 10, "10 * 2 * %s" % typeof_d)
        ]

        for v, t in test_cases:
            x = xnd(v)
            self.assertEqual(x.type, ndt(t))
            self.assertEqual(x.value, v)

    def test_int64(self):
        t = (1, -2, -3)
        typeof_t = "(int64, int64, int64)"

        test_cases = [
          ([0], "1 * int64"),
          ([0, 1], "2 * int64"),
          ([[0], [1]], "2 * 1 * int64"),

          (t, typeof_t),
          ([t] * 2, "2 * %s" % typeof_t),
          ([[t] * 2] * 10, "10 * 2 * %s" % typeof_t)
        ]

        for v, t in test_cases:
            x = xnd(v)
            self.assertEqual(x.type, ndt(t))
            self.assertEqual(x.value, v)

    def test_string(self):
        t = ("supererogatory", "exiguous")
        typeof_t = "(string, string)"

        test_cases = [
          (["mov"], "1 * string"),
          (["mov", "$0"], "2 * string"),
          ([["cmp"], ["$0"]], "2 * 1 * string"),

          (t, typeof_t),
          ([t] * 2, "2 * %s" % typeof_t),
          ([[t] * 2] * 10, "10 * 2 * %s" % typeof_t)
        ]

        for v, t in test_cases:
            x = xnd(v)
            self.assertEqual(x.type, ndt(t))
            self.assertEqual(x.value, v)

    def test_bytes(self):
        t = (b"lagrange", b"points")
        typeof_t = "(bytes, bytes)"

        test_cases = [
          ([b"L1"], "1 * bytes"),
          ([b"L2", b"L3", b"L4"], "3 * bytes"),
          ([[b"L5"], [b"none"]], "2 * 1 * bytes"),

          (t, typeof_t),
          ([t] * 2, "2 * %s" % typeof_t),
          ([[t] * 2] * 10, "10 * 2 * %s" % typeof_t)
        ]

        for v, t in test_cases:
            x = xnd(v)
            self.assertEqual(x.type, ndt(t))
            self.assertEqual(x.value, v)


class IndexTest(unittest.TestCase):

    def test_indexing(self):
        x = xnd([])
        self.assertRaises(IndexError, x.__getitem__, 0)
        self.assertRaises(IndexError, x.__getitem__, (0, 0))

        x = xnd([0])
        self.assertEqual(x[0], 0)

        self.assertRaises(IndexError, x.__getitem__, 1)
        self.assertRaises(IndexError, x.__getitem__, (0, 1))

        x = xnd([[0,1,2], [3,4,5]])
        self.assertEqual(x[0,0], 0)
        self.assertEqual(x[0,1], 1)
        self.assertEqual(x[0,2], 2)

        self.assertEqual(x[1,0], 3)
        self.assertEqual(x[1,1], 4)
        self.assertEqual(x[1,2], 5)

        self.assertRaises(IndexError, x.__getitem__, (0, 3))
        self.assertRaises(IndexError, x.__getitem__, (2, 0))

        t1 = (1.0, "capricious", (1, 2, 3))
        t2 = (2.0, "volatile", (4, 5, 6))

        x = xnd([t1, t2])
        self.assertEqual(x[0], t1)
        self.assertEqual(x[1], t2)

        self.assertEqual(x[0,0], 1.0)
        self.assertEqual(x[0,1], "capricious")
        self.assertEqual(x[0,2], (1, 2, 3))

        self.assertEqual(x[1,0], 2.0)
        self.assertEqual(x[1,1], "volatile")
        self.assertEqual(x[1,2], (4, 5, 6))

    def test_subview(self):
        # fixed
        x = xnd([["a", "b"], ["c", "d"]])
        self.assertEqual(x[0].value, ["a", "b"])
        self.assertEqual(x[1].value, ["c", "d"])

        # var
        x = xnd([["a", "b"], ["x", "y", "z"]])
        self.assertEqual(x[0].value, ["a", "b"])
        self.assertEqual(x[1].value, ["x", "y", "z"])


class TestSpec(unittest.TestCase):

    def __init__(self, *, constr,
                 values, value_generator,
                 indices_generator, indices_generator_args):
        super().__init__()
        self.constr = constr
        self.values = values
        self.value_generator = value_generator
        self.indices_generator = indices_generator
        self.indices_generator_args = indices_generator_args
        self.indices_stack = [None] * 8

    def log_err(self, value, depth):
        """Dump an error as a Python script for debugging."""

        sys.stderr.write("\n\nfrom xnd import *\n")
        sys.stderr.write("from test_xnd import NDArray\n")
        sys.stderr.write("lst = %s\n\n" % value)
        sys.stderr.write("x0 = xnd(lst)\n")
        sys.stderr.write("y0 = NDArray(lst)\n" % value)

        for i in range(depth+1):
            sys.stderr.write("x%d = x%d[%s]\n" % (i+1, i, itos(self.indices_stack[i])))
            sys.stderr.write("y%d = y%d[%s]\n" % (i+1, i, itos(self.indices_stack[i])))

        sys.stderr.write("\n")

    def run_single(self, nd, d, indices):
        """Run a single test case."""

        nd_exception = None
        try:
            nd_result = nd[indices]
        except Exception as e:
            nd_exception =  e

        def_exception = None
        try:
            def_result = d[indices]
        except Exception as e:
            def_exception = e

        if nd_exception or def_exception:
            if nd_exception is None and def_exception.__class__ is IndexError:
                # Example: type = 0 * 0 * int64
                if len(indices) <= nd.ndim:
                    return None, None

            self.assertIs(nd_exception.__class__, def_exception.__class__)
            return None, None

        if isinstance(nd_result, xnd):
            nd_value = nd_result.value
        elif np is not None and isinstance(nd_result, np.ndarray):
            nd_value = nd_result.tolist()
        else:
            nd_value = nd_result

        self.assertEqual(nd_value, def_result)
        return nd_result, def_result

    def run(self):
        def check(nd, d, value, depth):
            if depth > 3: # adjust for longer tests
                return

            g = self.indices_generator(*self.indices_generator_args)

            for indices in g:
                self.indices_stack[depth] = indices

                try:
                    next_nd, next_d = self.run_single(nd, d, indices)
                except Exception as e:
                    self.log_err(value, depth)
                    raise e

                if isinstance(next_d, list): # possibly None or scalar
                    check(next_nd, next_d, value, depth+1)

        for value in self.values:
            nd = self.constr(value)
            d = NDArray(value)
            check(nd, d, value, 0)

        for max_ndim in range(1, 5):
            for min_shape in (0, 1):
                for max_shape in range(1, 8):
                    for value in self.value_generator(max_ndim, min_shape, max_shape):
                        nd = self.constr(value)
                        d = NDArray(value)
                        check(nd, d, value, 0)


@unittest.skipIf(SKIP_LONG, "use --long argument to enable these tests")
class LongIndexSliceTest(unittest.TestCase):

    def test_subarray(self):
        # Multidimensional indexing
        t = TestSpec(constr=xnd,
                     values=FIXED_TEST_CASES,
                     value_generator=gen_fixed,
                     indices_generator=genindices,
                     indices_generator_args=())
        t.run()

        t = TestSpec(constr=xnd,
                     values=VAR_TEST_CASES,
                     value_generator=gen_var,
                     indices_generator=genindices,
                     indices_generator_args=())
        t.run()

    def test_slices(self):
        # Multidimensional slicing
        t = TestSpec(constr=xnd,
                     values=FIXED_TEST_CASES,
                     value_generator=gen_fixed,
                     indices_generator=randslices,
                     indices_generator_args=(3,))
        t.run()

        t = TestSpec(constr=xnd,
                     values=VAR_TEST_CASES,
                     value_generator=gen_var,
                     indices_generator=randslices,
                     indices_generator_args=(3,))
        t.run()

    def test_chained_indices_slices(self):
        # Multidimensional indexing and slicing, chained
        t = TestSpec(constr=xnd,
                     values=FIXED_TEST_CASES,
                     value_generator=gen_fixed,
                     indices_generator=gen_indices_or_slices,
                     indices_generator_args=())
        t.run()


        t = TestSpec(constr=xnd,
                     values=VAR_TEST_CASES,
                     value_generator=gen_var,
                     indices_generator=gen_indices_or_slices,
                     indices_generator_args=())
        t.run()

    def test_fixed_mixed_indices_slices(self):
        # Multidimensional indexing and slicing, mixed
        t = TestSpec(constr=xnd,
                     values=FIXED_TEST_CASES,
                     value_generator=gen_fixed,
                     indices_generator=mixed_indices,
                     indices_generator_args=(3,))
        t.run()

    def test_var_mixed_indices_slices(self):
        x = xnd([[1], [2, 3], [4, 5, 6]])

        indices = (0, slice(0,1,1))
        self.assertRaises(IndexError, x.__getitem__, indices)

        indices = (slice(0,1,1), 0)
        self.assertRaises(IndexError, x.__getitem__, indices)

    @unittest.skipIf(SKIP_BRUTE_FORCE, "use --all argument to enable these tests")
    def test_slices_brute_force(self):
        # Test all possible slices for the given ndim and shape
        t = TestSpec(constr=xnd,
                     values=FIXED_TEST_CASES,
                     value_generator=gen_fixed,
                     indices_generator=genslices_ndim,
                     indices_generator_args=(3, [3,3,3]))
        t.run()

        t = TestSpec(constr=xnd,
                     values=VAR_TEST_CASES,
                     value_generator=gen_var,
                     indices_generator=genslices_ndim,
                     indices_generator_args=(3, [3,3,3]))
        t.run()

    @unittest.skipIf(np is None, "numpy not found")
    def test_array_definition(self):
        # Test the NDArray definition against NumPy
        t = TestSpec(constr=np.array,
                     values=FIXED_TEST_CASES,
                     value_generator=gen_fixed,
                     indices_generator=mixed_indices,
                     indices_generator_args=(3,))
        t.run()


if __name__ == '__main__':
    unittest.main(verbosity=2)
