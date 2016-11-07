# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe import _
import frappe.utils
from frappe.utils import flt, cstr
from frappe.model.document import Document

class DignitySeniorCitizen(Document):
	def validate(self):
		if self.age < 60 or not self.age:
			frappe.throw(_("Age should be more than 60 for Senior Citizen"))
		if not self.tahsildar_state or not self.tahsildar_city or not self.tahsildar_centre:
			frappe.throw(_("State, City and Center are mandatory fields"))
		if self.tahsildar_state and self.tahsildar_city and self.tahsildar_centre:
			tahsildar = frappe.db.sql("""select naming_series,tahsildar_series_from,tahsildar_series_to,tahsildar_last_series from `tabDignity Tahsildar Master` where parent = %s and tahsildar_city = %s and tahsildar_centre = %s""",(self.tahsildar_state,self.tahsildar_city,self.tahsildar_centre))
			if tahsildar:
				naming_series = tahsildar[0][0]
				tahsildar_series_from = tahsildar[0][1]
				tahsildar_series_to = tahsildar[0][2]
				last_series_no = tahsildar[0][3]
			else:
				frappe.throw(_("Number series is not set up for State, City and Centre combination."))
		# Generate the card Number, validate range and Insert
		print (naming_series,tahsildar_series_from,tahsildar_series_to,last_series_no)
		new_series_no = last_series_no + 1
		if new_series_no > tahsildar_series_to:
			frappe.throw(_("You have used all existing series numbers in the setup. Please update series number in Master Set Up accordingly"))
		str_len_new_series_no = len(cstr(new_series_no))
		str_new_series_no = cstr(new_series_no)
		#zero padding
		if str_len_new_series_no < 5:
			no_of_leading_zeroes = 5 - str_len_new_series_no
			str_new_series_no.ljust(no_of_leading_zeroes,"0")
		new_card_no = naming_series + str_new_series_no
		self.new_series_no = new_series_no
		self.card_number = new_card_no
		#check if card number already exists to avoid data duplication
		card_check = frappe.db.sql("""select 'X' from `tabDignity Senior Citizen` where card_number = %s""",self.card_number)
		if card_check:
			frappe.throw(_("Senior Citizen Card No already exists"))
		if self.tahsildar_state and self.tahsildar_city and self.tahsildar_centre:
			frappe.db.sql("""update `tabDignity Tahsildar Master` set tahsildar_last_series = %s where parent = %s and tahsildar_city = %s and tahsildar_centre = %s""",(self.new_series_no,self.tahsildar_state,self.tahsildar_city,self.tahsildar_centre))

@frappe.whitelist()
def get_tahsildar(state,city,centre):
	conditions=""
	if state and city and centre:
		filters = {}
		filters["state"]= state
		filters["city"] = city
		filters["centre"] = centre
		if state:
			conditions += " and parent = %(state)s"
		if city:
			conditions += " and tahsildar_city = %(city)s"
		if centre:
			conditions += " and tahsildar_centre = %(centre)s"
		tahsildar = frappe.db.sql("""select tahsildar_no,naming_series from `tabDignity Tahsildar Master` where 1=1 %s""" % (conditions,),filters)
	return (tahsildar[0][0],tahsildar[0][1]) if tahsildar else ("None","MU")