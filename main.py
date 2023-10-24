import holidays
from conf import full_name, tempo_token, team_number, issue_id

from tempoapiclient import client_v4
from datetime import timedelta, date

month_no = 12
current_year = 2023
timeoff = []
holidays = holidays.country_holidays('MA')



def get_tempo_authenticated_client(token):
    return client_v4.Tempo(auth_token=token)

def get_myaccount_id(tempo):
    res = tempo.get_team_members(team_number)
    for rec in res:
        if rec['member']['displayName'] == full_name:
            return rec['member']['accountId']
    
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def check_worklog(tempo):
    start_date, end_date = get_start_and_end_dates(month_no=month_no)
    worklogs = tempo.get_worklogs(dateFrom=start_date.strftime('%Y-%m-%d'), dateTo=end_date.strftime('%Y-%m-%d'))
    print(worklogs)

def get_start_and_end_dates(month_no):
    start_date = date(current_year, month_no, 1)
    if month_no == 12: 
        next_month_no = 1
        year = current_year + 1
    else: 
        next_month_no = month_no + 1
    end_date = date(year, next_month_no, 1)
    return start_date, end_date


if __name__ ==  '__main__':

    res = []
    tempo = get_tempo_authenticated_client(tempo_token)
    account_id = get_myaccount_id(tempo)
    start_date, end_date = get_start_and_end_dates(month_no=month_no)
    for single_date in daterange(start_date, end_date):
        if single_date.weekday() < 5:
            if single_date in holidays or single_date.day in timeoff :
                continue
            data = {
                "authorAccountId": account_id,
                "description": "logged from API",
                "issueId": issue_id,
                "remainingEstimateSeconds": 0,
                "startDate": single_date.strftime("%Y-%m-%d"),
                "startTime": "08:00:00",
                "timeSpentSeconds": 3600 * 8
            }
            res.append(tempo.post(path='/worklogs', data=data))
    if all(res):
        print('log successful')
    else:
        print('log failed')

