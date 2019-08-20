import taskfunctions

def test_get_next_day_of():
    today = dt.datetime.today().date()
    tt_opts = ['month', 'quarter', 'year']
    due_dates = {}
    print('date', *tt_opts)
    for week in cal.monthcalendar(today.year, today.month):
        for day_num in week:
            if day_num != 0:
                today = today.replace(day=day_num)
                if today.weekday() < 5:
                    # business day
                    day_list = []
                    for tt in tt_opts:
                        day_list.append(taskfunctions._get_next_day_of(tt, today = today))
                    due_dates[today] = day_list
                    print(today, *day_list)