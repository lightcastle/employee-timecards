#!/usr/bin/env python
import sys
import datetime
import calendar
import gspread
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plot
import numpy

current=datetime.datetime.now()
date=str(current.month)+"-"+str(current.day)+"-"+str(current.year)

gc = gspread.login(sys.argv[1], sys.argv[2])
invoice_spreadsheet=gc.open("Invoices (Responses)")
time_spreadsheet=gc.open("Time Cards (Responses)")

timesheet=time_spreadsheet.worksheet("Form Responses")
invoice_sheet=invoice_spreadsheet.worksheet("Form Responses")
# The following two arrays set the initial data sets
employee_time = timesheet.get_all_values()
invoice_row_data = invoice_sheet.get_all_values()
#print employee_time
#print invoice_row_data

#delete first entry in "invoice_list" and "employee_time" because it's just header information
del invoice_row_data[0]
del employee_time[0]
#print invoice_row_data[0]
#print employee_time[0]
global_employee_time_cards=[]
global_invoice_array=[]

# temp_time_row_data array is used to filter out None values that for some reason appeared in the data.
# After the filter is done, it sets the good values into time_row_data
temp_time_row_data=[]
time_row_data=[]
temp_invoice_data=[]
invoice_data=[]


# This iterates through to add *all* rows in the time sheet spreadsheet to a temporary array
# It's temporary so that we can remove "None" values, which are showing up for some reason
for i in employee_time:
  if i[0]!="" and i[1]!="":
    temp_time_row_data.append(i)

# This adds only rows that are not filled with "None" data to the time_row_data list.
for x in temp_time_row_data:
  if x[0] != None and x[1] != None and x[0]!="" and x[1]!="":
   time_row_data.append(x)


for item in invoice_row_data:
  if item[0] != None and item[1] != None and item[0]!="" and item[1]!="":
    temp_invoice_data.append(item)



# Create Invoice class so you can instantiate a new invoice and not have to worry with things like "invoice[3]" to pull values
class Invoice:
  def __init__(self, invoice_number, customer_name, date, lead, amount, agreements_sold, service_type, callback, callback_date, callback_notes, no_money):
    self.invoice_number=int(invoice_number) #converts invoice_number data to integer, because it's imported as a string
    self.customer_name=customer_name
    self.amount=float(amount) # amount is floated because it's a decimal, otherwise you end up with a lot of rounded numbers.
    self.date=date
    self.lead=lead
    self.agreements_sold=int(agreements_sold)
    self.service_type=service_type
    self.callback=callback
    self.callback_date=callback_date
    self.callback_notes=callback_notes
    self.no_money=no_money 

# Create Employee class so you can instantiate employee time records without worryiing about things like "employee[5]" to pull values
class Employee:
  def __init__(self, employee_name, invoice_number): #, hours_sold, hours_billed, date):
    self.employee_name=employee_name
    self.invoice_number=int(invoice_number)
#    self.hours_sold=float(hours_sold)
#    self.hours_billed=float(hours_billed)
#    self.date=date

# The following two for loops iterate over the data we first pulled from the spreadsheet, and creates
# an array of employee time cards and an array of invoices, that will let us call invoice[3].customer_name, etc
for employee in time_row_data:
#  print employee
  stripped_date=employee[5].lstrip("'")
  new_employee_time_card=Employee(employee[1], employee[2]) #, employee[3], employee[4], stripped_date)
  global_employee_time_cards.append(new_employee_time_card)

for invoice in temp_invoice_data:
#  print invoice
  new_invoice=Invoice(invoice[2], invoice[1], invoice[3].lstrip("'"), invoice[4], invoice[5], invoice[6], invoice[7], invoice[8], invoice[9], invoice[10], invoice[11])
  global_invoice_array.append(new_invoice)


def filter_data_by_date_and_graph(year_or_month, unfiltered_invoice_array, unfiltered_employee_time_cards):
  invoice_array=[]
  employee_time_cards=[]

  monthly_invoice_array=[]
  monthly_time_cards_array=[] #this is a workaround to be able to properly calculate monthly average revenues per employee

  month=calendar.month_name[current.month]
  day_range=" 1-"+str(current.day)
  month_range="Jan-"+month[0:4]
  if year_or_month=="year":
    label_prefix="Jan-"+month
    save_prefix="/var/www/bluemtn/YTD-"
    extra_save=save_prefix+month
    for invoice in unfiltered_invoice_array:
#      print invoice.date[0:4], invoice.date, current.year
      if str(int(invoice.date[0:4]))==str(current.year):
        invoice_array.append(invoice)
    for employee in unfiltered_employee_time_cards:
#      if str(employee.date[0:4])==str(current.year):
      employee_time_cards.append(employee)

  elif year_or_month=="month":
    label_prefix=month+day_range
    save_prefix="/var/www/bluemtn/MTD-"
    extra_save=save_prefix+month
    for invoice in unfiltered_invoice_array:
#      print str(int(invoice.date[5:7])), str(current.month), invoice.date
      if str(int(invoice.date[5:7]))==str(current.month)  and str(int(invoice.date[0:4])) == str(current.year):
        invoice_array.append(invoice)
        monthly_invoice_array.append(invoice)
    for employee in unfiltered_employee_time_cards:
      employee_time_cards.append(employee) # a hash of objects, each of which consists of an employee name and an invoice

    for invoice in monthly_invoice_array:
      for employee in employee_time_cards:
        if invoice.invoice_number == employee.invoice_number:
          monthly_time_cards_array.append(employee)







#  print invoice_array
#  print employee_time_cards


  # create hashes that will be used for graphing. Hashes make the graphing easy because you can 
  # just do employee_invoices.keys() for the x axis and employee_invoices.values() for the bars that are graphed
  # If you want to add a graph in the future, you'd initialize a hash here for it, then add an .append to the 
  # third for loop below
  employee_invoices={}
  monthly_employee_invoices={} #this is used to calculate the monthly average revenues per employee
  total_revenue={}
  callbacks={}
  service_agreements={}
  average_rev={}
  no_money={}
  monthly_average_rev={}
  # Finds all unique employee names and adds them to the appropriate hash, which were created above
  for employee in employee_time_cards:
#    print employee.employee_name, "finitio"
    employee_invoices[employee.employee_name]=[]
    monthly_employee_invoices[employee.employee_name]=[]
    monthly_average_rev[employee.employee_name]=[]
    total_revenue[employee.employee_name]=0
    callbacks[employee.employee_name]=0
    service_agreements[employee.employee_name]=0
    average_rev[employee.employee_name]=0
    no_money[employee.employee_name]=0
  #print average_rev  

  # Appends the invoice numbers to the right employee who worked on the invoice, making a list of invoices per employee as a hash
### testing new functionality code below. not right excactly
  if year_or_month=="year":
    for employee_name in employee_invoices: #employee_invoices is a hash of employees with a list of invoices as array
      for worker in employee_time_cards:
        if employee_name==worker.employee_name:
          employee_invoices[employee_name].append(worker.invoice_number)
  elif year_or_month=="month":
    for employee_name in employee_invoices: #employee_invoices is a hash of employees with a list of invoices as array
      for worker in monthly_time_cards_array:
        if employee_name==worker.employee_name:
          employee_invoices[employee_name].append(worker.invoice_number)






#  if year_nvoice in employee_name:
#    for invoice in invoice_array:
#      if str(int(invoice.date[5:7]))==str(current.month):
#        monthly_invoice_array.append(invoice)
  print monthly_invoice_array
  print monthly_time_cards_array 
 
  # Searches for invoice numbers and adds the right revenue, callback and other information to a few hashes of employees
  # in order to graph the data.
  for invoice in invoice_array:
    for employee in employee_time_cards:
      if employee.invoice_number==invoice.invoice_number:
        total_revenue[employee.employee_name]+=invoice.amount
        service_agreements[employee.employee_name]+=invoice.agreements_sold
        average_rev[employee.employee_name]=(total_revenue[employee.employee_name])/len(employee_invoices[employee.employee_name])
        if invoice.callback=="yes":
          callbacks[employee.employee_name]+=1
        if invoice.no_money=="yes":
          no_money[employee.employee_name]+=1
        #print employee_invoices[employee.employee_name], len(employee_invoices[employee.employee_name])
  #    else:
  #      create error file saying data doesnt match
  #print average_rev

#  print no_money.keys()
#  print no_money.values()
#  print "revenue", total_revenue.keys(), total_revenue.values()
#  print "callbacks", callbacks.keys(), callbacks.values()
#  print "agreements", service_agreements.keys(), service_agreements.values()



  graph(total_revenue.keys(), total_revenue.values(), len(total_revenue.keys()), "Revenue", label_prefix+" Revenues\nper Employee", save_prefix+"Revenues", "yes", extra_save+"Revenues")
  graph(callbacks.keys(), callbacks.values(), len(callbacks.keys()), "Callbacks", label_prefix+" Callbacks\nper Employee", save_prefix+"Callbacks", "no", extra_save+"Callbacks")
  graph(service_agreements.keys(), service_agreements.values(), len(service_agreements.keys()), "Service Agreements", label_prefix+" Svc\n Agreements per Employee", save_prefix+"Agreements", "no", extra_save+"Agreements")
  graph(average_rev.keys(), average_rev.values(), len(average_rev.keys()), "Revenue Per Invoice", label_prefix+" Revenues Average", save_prefix+"Averages", "yes", extra_save+"Averages-wrongmonthly")
  graph(no_money.keys(), no_money.values(), len(no_money.keys()), "No Money Calls", label_prefix+" No Money Calls", save_prefix+"NoMoney", "no", extra_save+"NoMoney")


def graph(x_keys, bar_values, number, y_label, graph_title, save_name, has_dollars, old_records_save_name):
  
  # Much of the following is just copy/pasted from http://matplotlib.org/examples/api/barchart_demo.html with data substituted
  ind = numpy.arange(number)  # the x locations for the groups
  width = 0.35       # the width of the bars
  
  fig = plot.figure()
  ax = fig.add_subplot(111)
  new_bars=[]

  rects1 = ax.bar(ind, bar_values, width, color='#6699CC')
  
  # add some
  ax.set_ylabel(y_label)
  ax.set_title(graph_title)
  ax.set_xticks(ind+(width/2.0))
  ax.set_xticklabels( x_keys )
  ax.margins(.05)
  ax.set_xlim(-.5, number)
  if has_dollars=="yes":
    for item in ax.get_yticks():
      new_bars.append("$"+str(item))
    ax.set_yticklabels(new_bars)

  def autolabel(rects):
      # attach some text labels
      for rect in rects:
          height = rect.get_height()
          ax.text(rect.get_x()+(rect.get_width()/2.0), .8*height, '%d'%int(height), ha='center', va='bottom')


  autolabel(rects1)
  t=ax.title
  t.set_y(1.07)
  fig=plot.gcf()
  fig.set_size_inches(4,4)
  fig.tight_layout()
  plot.subplots_adjust(wspace = 0.05)
  plot.savefig(save_name, format="png")
  plot.savefig(old_records_save_name, format="png")

filter_data_by_date_and_graph("month", global_invoice_array, global_employee_time_cards)
filter_data_by_date_and_graph("year", global_invoice_array, global_employee_time_cards)


