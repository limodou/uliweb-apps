#coding=utf8
from uliweb.form import *

class JobForm(Form):
    def form_validate(self, data):
        from croniter import croniter
        from uliweb.utils import date

        errors = {}

        if 'time' in data:
            t = data['time']
            try:
                croniter(data['time'], date.now())
            except Exception as e:
                errors['time'] = 'Crontab 时间格式不正确'

        return errors