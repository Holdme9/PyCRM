from django import forms
from bootstrap_datepicker_plus.widgets import DatePickerInput


class DateRangeForm(forms.Form):
    start_date = forms.DateField(widget=DatePickerInput())
    end_date = forms.DateField(widget=DatePickerInput(range_from="start_date"))
