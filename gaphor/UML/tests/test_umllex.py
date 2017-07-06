#!/usr/bin/env python

# Copyright (C) 2007-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
Parsing of UML model elements from string tests.
"""

from __future__ import absolute_import
import unittest
from gaphor.UML.elementfactory import ElementFactory
from gaphor.UML.umllex import attribute_pat, operation_pat, parameter_pat
from gaphor.UML import uml2
from gaphor.UML.umllex import parse

def dump_prop(prop):
    m = attribute_pat.match(prop)
    #print m.groupdict()

def dump_oper(oper):
    m = operation_pat.match(oper)
    if m:
        g = m.group
    else:
        # set name to oper
        return
    #print g('vis'), g('name'), g('type'), g('mult_l'), g('mult_u'), g('tags')
    if g('params'):
        params = g('params')
        while params:
            m = parameter_pat.match(params)
            g = m.group
            #print ' ', g('dir') or 'in', g('name'), g('type'), g('mult_l'), g('mult_u'), g('default'), g('tags')
            params = g('rest')

dump_prop('#/name')
dump_prop('+ / name : str[1..*] = "aap" { static }')
dump_prop('+ / name : str[*] = "aap" { static }')

dump_oper('myfunc(aap:str = "aap", out two): type')
dump_oper('   myfunc2 ( ): type')
dump_oper('myfunc(aap:str[1] = "aap" { tag1, tag2 }, out two {tag3}): type')


factory = ElementFactory()

class AttributeTestCase(unittest.TestCase):
    """
    Parsing an attribute tests.
    """
    def setUp(self):
        pass


    def tearDown(self):
        factory.flush()


    def test_parse_property_simple(self):
        """Test simple property parsing
        """
        a = factory.create(uml2.Property)
        parse(a, 'myattr')
        self.assertFalse(a.isDerived)
        self.assertEqual('myattr', a.name)
        self.assertTrue(a.typeValue is None, a.typeValue)
        self.assertTrue(a.lowerValue is None, a.lowerValue)
        self.assertTrue(a.upperValue is None, a.upperValue)
        self.assertTrue(a.defaultValue is None, a.defaultValue)


    def test_parse_property_complex(self):
        """Test complex property parsing
        """
        a = factory.create(uml2.Property)

        parse(a,'+ / name : str[0..*] = "aap" { static }')
        self.assertEqual('public', a.visibility)
        self.assertTrue(a.isDerived)
        self.assertEqual('name', a.name)
        self.assertEqual('str', a.typeValue)
        self.assertEqual('0', a.lowerValue)
        self.assertEqual('*', a.upperValue)
        self.assertEqual('"aap"', a.defaultValue)


    def test_parse_property_invalid(self):
        """Test parsing property with invalid syntax
        """
        a = factory.create(uml2.Property)

        parse(a, '+ name = str[*] = "aap" { static }')
        self.assertEqual('+ name = str[*] = "aap" { static }', a.name)
        self.assertFalse(a.isDerived)
        self.assertTrue(not a.typeValue)
        self.assertTrue(not a.lowerValue)
        self.assertTrue(not a.upperValue)
        self.assertTrue(not a.defaultValue)



class AssociationEndTestCase(unittest.TestCase):
    """
    Parsing association end tests.
    """
    def setUp(self):
        pass

    def tearDown(self):
        factory.flush()

    def test_parse_association_end(self):
        """Test parsing of association end
        """
        a = factory.create(uml2.Association)
        p = factory.create(uml2.Property)
        p.association = a

        parse(p, 'end')
        self.assertEqual('end', p.name)
        self.assertTrue(not p.typeValue)
        self.assertTrue(not p.lowerValue)
        self.assertTrue(not p.upperValue)
        self.assertTrue(not p.defaultValue)


    def test_parse_multiplicity(self):
        """Test parsing of multiplicity
        """
        a = factory.create(uml2.Association)
        p = factory.create(uml2.Property)
        p.association = a
        parse(p, '0..2 { tag }')
        self.assertTrue(p.name is None)
        self.assertTrue(not p.typeValue)
        self.assertEqual('0', p.lowerValue)
        self.assertEqual('2', p.upperValue)
        self.assertTrue(not p.defaultValue)


    def test_parse_multiplicity2(self):
        """Test parsing of multiplicity with multiline constraints
        """
        a = factory.create(uml2.Association)
        p = factory.create(uml2.Property)
        p.association = a
        parse(p, '0..2 { tag1, \ntag2}')
        self.assertTrue(p.name is None)
        self.assertTrue(not p.typeValue)
        self.assertEqual('0', p.lowerValue)
        self.assertEqual('2', p.upperValue)
        self.assertTrue(not p.defaultValue)


    def test_parse_derived_end(self):
        """Test parsing derived association end
        """
        a = factory.create(uml2.Association)
        p = factory.create(uml2.Property)
        p.association = a
        parse(p, '-/end[*] { mytag}')
        self.assertEqual('private', p.visibility)
        self.assertTrue(p.isDerived)
        self.assertEqual('end', p.name)
        self.assertTrue(not p.typeValue)
        self.assertTrue(not p.lowerValue)
        self.assertEqual('*', p.upperValue)
        self.assertTrue(not p.defaultValue)


class OperationTestCase(unittest.TestCase):
    """
    Operation parsing tests.
    """

    def setUp(self):
        factory.flush()

    def tearDown(self):
        factory.flush()

    def test_parse_operation(self):
        """Test parsing simple operation
        """
        o = factory.create(uml2.Operation)
        parse(o, 'myfunc()')
        self.assertEqual('myfunc', o.name)
        self.assertTrue(not o.returnResult[0].typeValue)
        self.assertFalse(o.formalParameter)


    def test_parse_operation_return(self):
        """Test parsing operation with return value
        """
        o = factory.create(uml2.Operation)
        parse(o, '+ myfunc(): int')
        self.assertEqual('myfunc', o.name)
        self.assertEqual('int', o.returnResult[0].typeValue)
        self.assertEqual('public', o.visibility)
        self.assertTrue(not o.formalParameter)


    def test_parse_operation_2_params(self):
        """Test parsing of operation with two parameters
        """
        o = factory.create(uml2.Operation)
        parse(o, '# myfunc2 (a: str, b: int = 3 {  static}): float')
        self.assertEqual('myfunc2', o.name)
        self.assertEqual('float', o.returnResult[0].typeValue)
        self.assertEqual('protected', o.visibility)
        self.assertEqual(2, len(o.formalParameter))
        self.assertEqual('a', o.formalParameter[0].name)
        self.assertEqual('str', o.formalParameter[0].typeValue)
        self.assertTrue(o.formalParameter[0].defaultValue is None)
        self.assertEqual('b', o.formalParameter[1].name)
        self.assertEqual('int', o.formalParameter[1].typeValue)
        self.assertEqual('3', o.formalParameter[1].defaultValue)


    def test_parse_operation_1_param(self):
        """Test parsing of operation with one parameter
        """
        o = factory.create(uml2.Operation)
        parse(o, '- myfunc2 (a: node): double')
        self.assertEqual('myfunc2', o.name)
        self.assertEqual('double', o.returnResult[0].typeValue)
        self.assertEqual('private', o.visibility)
        self.assertEqual(1, len(o.formalParameter))
        self.assertEqual('a', o.formalParameter[0].name)
        self.assertEqual('node', o.formalParameter[0].typeValue)
        self.assertTrue(o.formalParameter[0].defaultValue is None)


    def test_parse_operation_invalid_syntax(self):
        """Test operation parsing with invalid syntax
        """
        o = factory.create(uml2.Operation)
        parse(o, '- myfunc2: myType2')
        self.assertEqual('- myfunc2: myType2', o.name)


# vim:sw=4:et:ai
