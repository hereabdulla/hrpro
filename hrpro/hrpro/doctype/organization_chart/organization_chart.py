# -*- coding: utf-8 -*-
# Copyright (c) 2021, TeamPRO and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
# from pyflowchart import *

class OrganizationChart(Document):
	pass

# @frappe.whitelist()
# def flowchart():
# 	st = StartNode('a_pyflow_test')
# 	op = OperationNode('do something')
# 	cond = ConditionNode('Yes or No?')
# 	io = InputOutputNode(InputOutputNode.OUTPUT, 'something...')
# 	sub = SubroutineNode('A Subroutine')
# 	e = EndNode('a_pyflow_test')

# 	# define the direction the connection will leave the node from
# 	sub.set_connect_direction("right")

# 	st.connect(op)
# 	op.connect(cond)
# 	cond.connect_yes(io)
# 	cond.connect_no(sub)
# 	sub.connect(op)
# 	io.connect(e)

# 	fc = Flowchart(st)
# 	print(fc.flowchart())