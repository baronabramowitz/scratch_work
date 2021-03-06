from datetime import date as _pythondate
from datetime import timedelta, datetime
import re
from math import sqrt

from abc import ABCMeta, abstractmethod
import pandas as pd
import numpy as np
import unittest

class CummutativeAddition:
    
    __metaclass__ = ABCMeta

    @abstractmethod
    def __neg__(self):
        raise NotImplementedError

    @abstractmethod
    def __abs__(self):
        raise NotImplementedError

    @abstractmethod
    def __add__(self, other_value):
        raise NotImplementedError

    @abstractmethod
    def __rsub__(self, other_value):
        '''__rsub__ has to be defined to handle right side subtraction since
        subtraction otherwise is specified at the left value.
        '''
        raise NotImplementedError

    def __radd__(self, other_value):
        return  self.__add__(other_value)

    def __sub__(self, other_value):
        return self.__add__(-other_value)

    def __iadd__(self, other_value):
        return  self.__add__(other_value)

    def __isub__(self, other_value):
        return self.__add__(-other_value)


class CummutativeMultiplication:
    

    __metaclass__ = ABCMeta

    @abstractmethod
    def __mul__(self, other_value):
        raise NotImplementedError

    @abstractmethod
    def __div__(self, other_value):
        raise NotImplementedError

    @abstractmethod
    def __rdiv__(self, other_value):
        raise NotImplementedError

    def __rmul__(self, other_value):
        return self.__mul__(other_value)


class Power:
    

    __metaclass__ = ABCMeta

    @abstractmethod
    def __pow__(self, other_value):
        raise NotImplementedError

    @abstractmethod
    def __rpow__(self, other_value):
        raise NotImplementedError

    def __ipow__(self, other_value):
        return self.__pow__(other_value)


if __name__ == '__main__':
    import doctest
    doctest.testmod()


class BankDateError(Exception):
    '''A class to implement error messages from class BankDate.'''
    pass


class TimePeriod(CummutativeAddition, CummutativeMultiplication):
    
    def __init__(self, period):
        
        self._count = None
        self._unit = None
        if isinstance(period,  TimePeriod):
            self._count = period.count
            self._unit = period.unit
        elif isinstance(period,  str):
            validate_period_ok = re.search('^(-?\d*)([d|w|m|y])$', period)
            if validate_period_ok:
                self._count, self._unit = validate_period_ok.groups()
                self._count = int(self._count)

    def __nonzero__(self):
        return 0 if self._count == None else 1

    def __str__(self):
        
        return '%s%s' % (self._count,  self._unit)

    __repr__ = __str__

    def __abs__(self):
        result = self.__class__(self)
        result.count = abs(result.count)
        return result

    def __neg__(self):
        result = self.__class__(self)
        result.count = -result.count
        return result

    def __add__(self, added_value):
       
        result = self.__class__(self)
        if isinstance(added_value, int):
            result.count += added_value
            return result
        if isinstance(added_value, TimePeriod):
            result.count += added_value.count
            return result

    def __rsub__(self, added_value):
        
        return self.__add__(- added_value)

    def __mul__(self, value):
        if isinstance(value, int):
            result = self.__class__(self)
            result.count *= value
            return result

    def __div__(self, value):
        
        if isinstance(value, int):
            result = self.__class__.__init__(self)
            result.count *= value
            return result

    def __rdiv__(self, other_value):
        return

    def __cmp__(self, period):
     
        if isinstance(period,  TimePeriod):
            if self.unit == period.unit:
                if self.count == period.count:
                    return 0
                elif self.count < period.count:
                    return -1
                elif self.count > period.count:
                    return 1
            else:
                raise BankDateError(
                'Non comparable units (%s) vs (%s)'
                % (self.unit,  period.unit))
        else:
            raise BankDateError(
            'Can not compare a TimePeriod with %s of type %s'
            % (period,  type(period)))

    def _get_count(self):
        
        return self._count

    def _set_count(self, value):
        '''set value of poperty count, type integer.'''
        if isinstance(value, int):
            self._count = value
        else:
            raise BankDateError('Value must be an integer, not (%s) of type %s'
                                    % (value,  type(value)))

    count = property(_get_count, _set_count)

    def _get_unit(self):
        '''Unit part [y(ears), m(onths) or d(ays)] of TimePeriod.
        '''
        return self._unit

    unit = property(_get_unit)


class BankDate(_pythondate):

    def __new__(self, bank_date=_pythondate.today()):
        day = None
        if isinstance(bank_date, str):
            try:
                day = datetime.strptime(bank_date, "%Y-%m-%d").date()
            except:
                pass
        elif isinstance(bank_date, _pythondate):
            day = bank_date
        elif isinstance(bank_date, BankDate):
            day = bank_date.date()
        if day:
            return super(BankDate, self).__new__(self,
                                                 day.year,
                                                 day.month,
                                                 day.day
                                                 )
        else:
            return None

    def __str__(self):
        return '%4d-%02d-%02d' % (self.year, self.month, self.day)

    __repr__ = __str__

    def __add__(self, period):
        '''A TimePeriod can be added to a BankDate
        '''
        period = TimePeriod(period)
        if period:
            if period.unit == 'y':
                return self.__class__(self).add_years(period.count)
            elif period.unit == 'm':
                return self.__class__(self).add_months(period.count)
            elif period.unit == 'w':
                return self.__class__(self).add_days(7 * period.count)
            elif period.unit == 'd':
                return self.__class__(self).add_days(period.count)

    def __radd__(self, period):
        '''A BankDate can be added to a TimePeriod
        '''
        return self.__add__(period)

    def __iadd__(self, period):
        '''A TimePeriod can be added to a BankDate
        '''
        return self.__add__(period)

    def __sub__(self, value):
        '''A BankDate can be subtracted either a TimePeriod or a BankDate
        giving a BankDate or the number of days between the 2 BankDates
        '''
        period = TimePeriod(value)
        if period:
            return self.__class__(self).__add__(-period)
        else:
            return -self.nbr_of_days(value)

    def __rsub__(self, date):
        '''A TimePeriod or a BankDate can be subtracted a BankDate giving a
        BankDate or the number of days between the 2 BankDates
        '''
        return self.__sub__(date)

    @staticmethod
    def ultimo(nbr_month):
        '''Return last day of month for a given number of month.

        :param nbr_month: Number of month
        :type nbr_month: int
        '''
        if isinstance(nbr_month, int):
            ultimo_month = {2: 28, 4: 30, 6: 30, 9: 30, 11: 30}
            if nbr_month in ultimo_month:
                return ultimo_month[nbr_month]
            else:
                return 31

    def is_ultimo(self):
        '''Identifies if BankDate is ultimo'''
        return BankDate.ultimo(self.month) == self.day

    def add_months(self, nbr_months):
        '''Adds nbr_months months to the BankDate.

        :param nbr_months: Number of months to be added
        :type nbr_months: int
        '''
        if isinstance(nbr_months, int):
            totalmonths = self.month + nbr_months
            year = self.year + totalmonths // 12
            if not totalmonths % 12:
                year -= 1
            month = totalmonths % 12 or 12
            day = min(self.day, BankDate.ultimo(month))
            return BankDate(_pythondate(year, month, day))

    def add_years(self, nbr_years):
        '''Adds nbr_years years to the BankDate.

        :param nbr_years: Number of years to be added
        :type nbr_years: int

         '''
        if isinstance(nbr_years, int):
            result = _pythondate(self.year + nbr_years, self.month, self.day)
            return BankDate(result)

    def add_days(self, nbr_days):
        '''Adds nbr_days days to the BankDate.

        :param nbr_days: Number of days to be added
        :type nbr_days: int
         '''
        if isinstance(nbr_days, int):
            result = _pythondate(self.year, self.month, self.day) + timedelta(nbr_days)
            return BankDate(result)

    def find_next_banking_day(self, nextday=1, holidaylist=()):
        
        if nextday not in (-1, 1):
            raise BankDateError(
            'The nextday must be  in (-1, 1), not %s of type %s'
            % (nextday, type(nextday)))
        lst = [BankDate(d).__str__() for d in holidaylist]
        date = self
        for i in range(30):
            if date.isoweekday() < 6 and str(date) not in lst:
                break
            date = date.add_days(nextday)
        return date

    def adjust_to_bankingday(self, daterolling='Actual', holidaylist=()):
        

        def actual_daterolling(holidaylist):
            '''Implement date rolling method Actual, ie no change
            '''
            return self

        def following_daterolling(holidaylist):
            '''Implement date rolling method Following
            '''
            return self.find_next_banking_day(1, holidaylist)

        def previous_daterolling(holidaylist):
            '''Implement date rolling method Previous
            '''
            return self.find_next_banking_day(-1, holidaylist)

        def modified_following_daterolling(holidaylist):
            '''Implement date rolling method Modified Following
            '''
            next_bd = self.find_next_banking_day(1, holidaylist)
            if self.month == next_bd.month:
                return next_bd
            else:
                return self.find_next_banking_day(-1, holidaylist)

        def modified_previous_daterolling(holidaylist):
            '''Implement date rolling method Modified Previous
            '''
            next_bd = self.find_next_banking_day(-1, holidaylist)
            if self.month == next_bd.month:
                return next_bd
            else:
                return self.find_next_banking_day(1, holidaylist)

        daterolling_dict = {
            'Actual':             actual_daterolling,
            'Following':          following_daterolling,
            'Previous':           previous_daterolling,
            'ModifiedFollowing':  modified_following_daterolling,
            'ModifiedPrevious':   modified_previous_daterolling,
            }
        if daterolling in daterolling_dict.keys():
            return daterolling_dict[daterolling](holidaylist)
        else:
            raise BankDateError(
            'The daterolling must be one of %s, not %s of type %s' \
            % (daterolling_dict.keys(), daterolling, type(daterolling)))

    def weekday(self, as_string=False):
        '''
        :param as_string: Return weekday as a number or a string
        :type as_string: Boolean
        :Return: day as a string or a day number of week, 0 = Monday etc
        '''
        if as_string:
            return self.strftime('%a')
        else:
            return self.weekday()

    def first_day_in_month(self):
        ''':Return: first day in month for this BankDate as BankDate
        '''
        day = self.day
        return self + '%sd' % (1 - day)

    def next_imm_date(self, future=True):
        '''An IMM date is the 3. wednesday in the months march, june,
        september and december

        reference: http://en.wikipedia.org/wiki/IMM_dates

        :Return: Next IMM date for BankDate as BankDate
        '''
        month = self.month
        if future:
            add_month = 3 - (month % 3)
        else:
            add_month = - ((month % 3) or 3)
        # First day in imm month
        out_date = self.first_day_in_month() + '%sm' % add_month
        add_day = 13 + (9 - out_date.weekday()) % 6
        out_date += '%sd' % add_day
        return out_date

    def nbr_of_months(self, date):
        '''
        :param date: date
        :type date: BankDate
        :return: The number of months between this bankingday and a date
        '''
        date = BankDate(date)
        if self.__str__() < date.__str__():
            date_min, date_max = self, date
            sign = +1
        else:
            date_min, date_max = date, self
            sign = -1
        nbr_month = (date_max.year - date_min.year) * 12 \
                    + date_max.month - date_min.month
        if date_max.day >= date_min.day:
            return sign * nbr_month
        else:
            return sign * (nbr_month - 1)

    def nbr_of_years(self, date):
        '''
        :param date: date
        :type date: BankDate
        :return: The number of years between this bankingday and a date
        '''
        nom = self.nbr_of_months(date)
        if nom > 0:
            return int(nom / 12)
        else:
            return - int(-nom / 12)

    def nbr_of_days(self, value):
        '''
        :param date: date
        :type date: BankDate
        :return: The number of days between this bankingday and a date
        '''
        bankdate = BankDate(value)
        if bankdate:
            # Subtraction is defined for _pythondate
            return -super(BankDate, self).__sub__(bankdate).days


def daterange_iter(
        enddate_or_integer,
        start_date=BankDate(),
        step='1y',
        keep_start_date=True,
        daterolling='Actual',
        holidaylist=()
        ):
    
    s_date = BankDate(start_date)
    step = TimePeriod(step)
    if isinstance(enddate_or_integer,  int):
        e_date = s_date + enddate_or_integer * step
    else:
        e_date = BankDate(enddate_or_integer)
    if e_date < s_date:
        s_date, e_date = e_date, s_date
    step.count = -abs(step.count)
    nbr_periods = 0
    tmp_date = e_date
    while tmp_date > s_date:
        yield tmp_date.adjust_to_bankingday(daterolling, holidaylist)
        nbr_periods += 1
        tmp_date = e_date + nbr_periods * step
    if keep_start_date:
        yield s_date.adjust_to_bankingday(daterolling, holidaylist)


def daterange(
        enddate_or_integer,
        start_date=BankDate(),
        step='1y',
        keep_start_date=True,
        daterolling='Actual',
        holidaylist=()
        ):
    
    return sorted(daterange_iter(enddate_or_integer, start_date, step,
                    keep_start_date, daterolling, holidaylist))


def period_count(end_date, start_date=BankDate(), period='1y'):

    return len(list(daterange_iter(end_date,  start_date, period,  False)))

if __name__ == '__main__':
    import doctest
    doctest.testmod()

def payment_dates(dateval, step):
    #step = (input('How often does this instrument pay a cash flow?  '))
    #Steps in number of months or years
    # e.g. '6m', '3m', '2y'
    #dateval = BankDate(input('What is the maturity date of this instrument?   '))
    #dateval as maturity date of instrument
    new_dates = []
    for date in daterange(dateval, step ='6m'):
        if datetime.weekday(date) == 6:
            date = date + '1d'
            new_dates.append(date)
        elif datetime.weekday(date) == 5:
            date = date + '2d'
            new_dates.append(date)
        else:
            new_dates.append(date)
    return(new_dates)

def days_to_payment(mat_date, pay_step):
    #
    #
    step = pay_step
    dateval = mat_date
    new_dates = payment_dates(dateval, step)
    days_to_payment = []
    for date in new_dates:
        days = BankDate().nbr_of_days(date)
        days_to_payment.append(days)
    return (days_to_payment)    

def value_bond(face_value,maturity_date,coupon_rate,payments_per_year,bond_rating,bond_type):
    pv_fcf = []
    """face_value = float(input('What is the face value?   '))
    maturity_date = BankDate(input('On what date does the bond mature YYYY-MM-DD?   '))
    coupon_rate = float(input('What is the Coupon Rate as a percentage?   '))
    payments_per_year = int(input('How many payments are made per year?   '))
    discount_rate = (float(input('What is the discount rate as a percentage?   '))/100)"""
    #if bond_type = 'Corporate':
    #To build out non corporate bond types
    discount_rates = yesterdays_yield_close_values_corp
    #else:
    #    discount_rate = yesterdays_yield_close_values_notcorp[bond_rating]
    bond_maturity_remaining = (BankDate().nbr_of_days(maturity_date))/365
    if bond_maturity_remaining < 2:
        two_string = str('2yr_' + str(bond_rating))
        disc_rate_two = discount_rates.at[0,two_string]
        disc_rate_under_two = disc_rate_two * (2 / 3)
        discount_rate = disc_rate_under_two

    elif 2 < bond_maturity_remaining < 5:
        proportion_two_year_rate = (bond_maturity_remaining - 2)/3
        proportion_five_year_rate = (5 - bond_maturity_remaining)/3
        two_string = str('2yr_' + str(bond_rating))
        five_string = str('5yr_' + str(bond_rating))
        disc_rate_two = discount_rates.at[0,two_string]
        disc_rate_five = discount_rates.at[0,five_string]
        discount_rate = disc_rate_two * proportion_two_year_rate + disc_rate_five * proportion_five_year_rate

    elif 5 < bond_maturity_remaining < 10:
        proportion_five_year_rate = (bond_maturity_remaining - 5)/5
        proportion_ten_year_rate = (10 - bond_maturity_remaining)/5
        five_string = str('5yr_' + str(bond_rating))
        ten_string = str('10yr_' + str(bond_rating))
        disc_rate_five = discount_rates.at[0,five_string]
        disc_rate_ten = discount_rates.at[0,ten_string]
        discount_rate = disc_rate_five * proportion_five_year_rate + disc_rate_ten * proportion_ten_year_rate

    elif 10 < bond_maturity_remaining < 20:
        proportion_ten_year_rate = (bond_maturity_remaining - 10)/10
        proportion_twenty_year_rate = (20 - bond_maturity_remaining)/10
        ten_string = str('10yr_' + str(bond_rating))
        twenty_string = str('20yr_' + str(bond_rating))
        disc_rate_ten = discount_rates.at[0,ten_string]
        disc_rate_twenty = discount_rates.at[0,twenty_string]
        discount_rate = disc_rate_ten * proportion_ten_year_rate + disc_rate_twenty * proportion_twenty_year_rate

    elif 20 < bond_maturity_remaining:
        twenty_string = str('20yr_' + str(bond_rating))
        disc_rate_twenty = discount_rates.at[0,twenty_string]
        disc_rate_over_twenty = disc_rate_twenty * (6 / 5)


    payment_step = str(payments_per_year/12) + 'm'
    if payments_per_year == 0:
        coupon_payment = 0
    else:
        coupon_payment = ((coupon_rate/100)*face_value)/payments_per_year
    days_to_payments = days_to_payment(maturity_date,payment_step)
    del days_to_payments[0]
    #print (days_to_payments)
    for day_count in days_to_payments:
        if day_count == max(days_to_payments):
            pv_cf = (coupon_payment + face_value)\
            /((1+(discount_rate/100/365))**day_count)
            pv_fcf.append(pv_cf)
        elif day_count != 0 and day_count != max(days_to_payments):
            pv_cf = coupon_payment/((1+(discount_rate/100/365))**day_count)
            pv_fcf.append(pv_cf)
        else:
            pass
    #print(pv_fcf)
    #print (len(pv_fcf))
    bond_val = sum(pv_fcf)
    #print('Bond Value:' + str(bond_val))
    return (bond_val, pv_fcf, days_to_payments, bond_maturity_remaining, discount_rate)

def value_bond_var(face_value,maturity_date,coupon_rate,payments_per_year,discount_rate):
    pv_fcf = []
    bond_maturity_remaining = (BankDate().nbr_of_days(maturity_date))/365
    payment_step = str(payments_per_year/12) + 'm'
    if payments_per_year == 0:
        coupon_payment = 0
    else:
        coupon_payment = ((coupon_rate/100)*face_value)/payments_per_year
    days_to_payments = days_to_payment(maturity_date,payment_step)
    del days_to_payments[0]
    #print (days_to_payments)
    for day_count in days_to_payments:
        if day_count == max(days_to_payments):
            pv_cf = (coupon_payment + face_value)\
            /((1+(discount_rate/100/365))**day_count)
            pv_fcf.append(pv_cf)
        elif day_count != 0 and day_count != max(days_to_payments):
            pv_cf = coupon_payment/((1+(discount_rate/100/365))**day_count)
            pv_fcf.append(pv_cf)
        else:
            pass
    bond_val = sum(pv_fcf)
    return (bond_val, pv_fcf, days_to_payments, bond_maturity_remaining, discount_rate)

def generate_portfolio(csv_location):
    portfolio = pd.read_csv(csv_location,\
                       header = 0,\
                       delimiter = ',',\
                       converters = {'face_value':np.float64,'maturity_date':str,'coupon_rate':np.float64,\
                                     'payments_per_year':np.float64,'bond_rating':str,'bond_type':str
                                    }
                       )
    return portfolio

def value_portfolio(csv_location):
    #csv_location = str(input('What is the file path?'))
    bond_val_portfolio = []
    bond_maturity_set = []
    portfolio = generate_portfolio(csv_location)
    for bond in zip(portfolio['face_value'],portfolio['maturity_date'],portfolio['coupon_rate'],\
                   portfolio['payments_per_year'],portfolio['bond_rating'],portfolio['bond_type']):
        bond_val = value_bond(*bond)[0]
        bond_maturity_set.append(value_bond(*bond)[3])
        bond_val_portfolio.append(bond_val)
    portfolio_val = sum(bond_val_portfolio)
    #print ('Portfolio Value:',portfolio_val)
    return (portfolio_val, bond_val_portfolio, bond_maturity_set)

def duration_bond(face_value,maturity_date,coupon_rate,payments_per_year,bond_rating,bond_type):
    value_bond_output_db = value_bond(face_value,maturity_date,coupon_rate,payments_per_year,bond_rating,bond_type)
    days_to_payments = value_bond_output_db[2]
    pv_fcf = value_bond_output_db[1]
    bond_val = value_bond_output_db[0]
    intermediate_dur_calcs = []
    years_to_payments = [ days / 365 for days in days_to_payments ]
    #print(years_to_payments)
    cfs = list(zip(pv_fcf,years_to_payments))
    for cf in cfs:
        inter_dur_calc = cf[0]*cf[1]
        intermediate_dur_calcs.append(inter_dur_calc)
        
    #print(intermediate_dur_calcs)
    #print(sum(intermediate_dur_calcs))
    bond_duration = sum(intermediate_dur_calcs)/bond_val
    mm_duration = bond_duration/(1 + value_bond_output_db[4] / 100)
    #print('Bond Duration: ',bond_duration, 'Modified Duration',mm_duration)
    return {'Bond Duration' : bond_duration, 'Modified Duration' : mm_duration}

def portfolio_duration(csv_location):
    bond_dur_portfolio=[]
    mm_bond_dur_portfolio=[]
    weighted_bond_dur_portfolio = []
    weighted_mm_bond_dur_portfolio = []
    portfolio = generate_portfolio(csv_location)
    val_portfolio_output = value_portfolio(csv_location)
    for bond in zip(portfolio['face_value'],portfolio['maturity_date'],portfolio['coupon_rate'],\
                   portfolio['payments_per_year'],portfolio['bond_rating'],portfolio['bond_type']):
        bond_dur = duration_bond(*bond)['Bond Duration']
        bond_dur_portfolio.append(bond_dur)
        mm_bond_dur = duration_bond(*bond)['Modified Duration']
        mm_bond_dur_portfolio.append(mm_bond_dur)
    bond_dur_val_zip = list(zip(bond_dur_portfolio,val_portfolio_output[1],mm_bond_dur_portfolio))
    for group in bond_dur_val_zip:
        scale_bond_dur_by_portfolio_value = group[0]*group[1]/val_portfolio_output[0]
        weighted_bond_dur_portfolio.append(scale_bond_dur_by_portfolio_value)
        scale_mm_bond_dur_by_portfolio_value = group[2]*group[1]/val_portfolio_output[0]
        weighted_mm_bond_dur_portfolio.append(scale_mm_bond_dur_by_portfolio_value)
    portfolio_dur = sum(weighted_bond_dur_portfolio)
    mm_portfolio_dur = sum(weighted_mm_bond_dur_portfolio)
    #print ('Portfolio Duration:',portfolio_dur,'Modified Portfolio Duration:',mm_portfolio_dur)
    return {'Portfolio Duration' : portfolio_dur, 'Modified Portfolio Duration' : mm_portfolio_dur}

def convexity_bond(face_value,maturity_date,coupon_rate,payments_per_year,bond_rating,bond_type):
    value_bond_output_cb = value_bond(face_value,maturity_date,coupon_rate,payments_per_year,bond_rating,bond_type)
    days_to_payments = value_bond_output_cb[2]
    pv_fcf = value_bond_output_cb[1]
    bond_val = value_bond_output_cb [0]
    intermediate_conv_calcs = []
    start_int = 1
    years_to_payments = [days/365 for days in days_to_payments]
    cfs = list(zip(pv_fcf,years_to_payments))
    for pv_cf in cfs:
        inter_conv_calc =  (pv_cf[0])*(pv_cf[1]**2+pv_cf[1])
        start_int = start_int +1
        intermediate_conv_calcs.append(inter_conv_calc)
        #print(inter_conv_calc)
        
    #print(intermediate_conv_calcs)
    #print(sum(intermediate_conv_calcs))
    bond_convexity = sum(intermediate_conv_calcs) / \
                    ( bond_val * ( 1 + value_bond_output_cb[4] / 100) **2 )
    #print('Bond Convexity: ',bond_convexity)
    return bond_convexity

def convexity_portfolio(csv_location):
    bond_conv_portfolio = []
    weighted_bond_conv_portfolio = []
    portfolio = generate_portfolio(csv_location)
    val_portfolio_output = value_portfolio(csv_location)
    for bond in zip(portfolio['face_value'],portfolio['maturity_date'],portfolio['coupon_rate'],\
                   portfolio['payments_per_year'],portfolio['bond_rating'],portfolio['bond_type']):
        bond_conv = convexity_bond(*bond)
        bond_conv_portfolio.append(bond_conv)
    bond_conv_val_zip = list(zip(bond_conv_portfolio,val_portfolio_output[1]))
    for entry in bond_conv_val_zip:
        scale_bond_conv_by_portfolio_value = entry[0]*entry[1]/val_portfolio_output[0]
        weighted_bond_conv_portfolio.append(scale_bond_conv_by_portfolio_value)
    portfolio_convexity = sum(weighted_bond_conv_portfolio)
    return portfolio_convexity

def generate_yield_comparison_table_raw(csv_location):
    """Builds a table containing daily 
    yield quotes of corporate bonds
    """
    daily_yield_change_array = pd.read_csv(csv_location,\
                       header = 0,\
                       delimiter = ',',\
                       converters = {'Date':str,'2yr AA':np.float64,'2yr A':np.float64,\
                            '5yr AAA':np.float64,'5yr AA':np.float64, '5yr A':np.float64,\
                            '10yr AAA':np.float64, '10yr AA':np.float64,'10yr A':np.float64,\
                             '20yr AAA':np.float64,'20yr AA':np.float64, '20yr A':np.float64,\
                                    }
                       )
    return daily_yield_change_array

yesterdays_yield_close_values_corp = generate_yield_comparison_table_raw ('/Users/baronabramowitz/Desktop/corporate_bond_yields_daily_values.csv').iloc[[0]] 

def value_at_risk_yield_change_upper_bound_by_rating(csv_location, loss_percentile):
    """Takes a table of daily bond yield quotes, 
    extracts the quotes for the ratings,
    (currently supported bond ratings limited to                    
                        'Corporate 2yr AA','Corporate 2yr A',
    'Corporate 5yr AAA','Corporate 5yr AA', 'Corporate 5yr A',
    'Corporate 10yr AAA','Corporate 10yr AA','Corporate 10yr A', 
    'Corporate 20yr AAA','Corporate 20yr AA', 'Corporate 20yr A'
    )
    determines the lower bound for the inputted percentile 
    (percentile as a whole number, eg 95th percentile as 95 not .95)
    Intended to be run before trading, once a trading day and the VaR bounds should be stored
    """
    daily_yield_change_array = generate_yield_comparison_table_raw(csv_location)
    upper_bounds = []
    bond_ratings_set = ['2yr_AA','2yr_A',\
        '5yr_AAA','5yr_AA', '5yr_A',\
        '10yr_AAA','10yr_AA','10yr_A',\
        '20yr_AAA','20yr_AA', '20yr_A']
    for bond_rating_val in bond_ratings_set:
        daily_yield_change_rating_specific_no_date = daily_yield_change_array[bond_rating_val]
        upper_bound = np.percentile(daily_yield_change_rating_specific_no_date,loss_percentile)
        upper_bounds.append(upper_bound)
    upper_bound_set = dict(zip(bond_ratings_set,upper_bounds))
    return upper_bound_set

def value_at_risk_single_bond(face_value,maturity_date,coupon_rate,payments_per_year,bond_rating,bond_type,csv_location,loss_percentile):
    bond_val = value_bond(face_value,maturity_date,coupon_rate,payments_per_year,bond_rating,bond_type)[0]
    bond_maturity_remaining = (BankDate().nbr_of_days(maturity_date))/365
    if bond_maturity_remaining < 2:
        bond_rating = str('2yr_' + bond_rating)
        discount_rate = yesterdays_yield_close_values_corp.at[0,bond_rating]
    elif 2 <= bond_maturity_remaining <= 3.5:
        bond_rating = str('2yr_' + bond_rating)
        discount_rate = yesterdays_yield_close_values_corp.at[0,bond_rating]
    elif 3.5 < bond_maturity_remaining <= 7.5:
        bond_rating = str('5yr_' + bond_rating)
        discount_rate = yesterdays_yield_close_values_corp.at[0,bond_rating]
    elif 7.5 < bond_maturity_remaining <= 15:
        bond_rating = str('10yr_' + bond_rating)
        discount_rate = yesterdays_yield_close_values_corp.at[0,bond_rating]
    elif 15 < bond_maturity_remaining:
        bond_rating = str('20yr_' + bond_rating)
        discount_rate = yesterdays_yield_close_values_corp.at[0,bond_rating]
    else:
        print('WTF')

    upper_bound = value_at_risk_yield_change_upper_bound_by_rating(csv_location,loss_percentile)[bond_rating]
    new_discount_rate = discount_rate + upper_bound
    new_bond_val = value_bond_var(face_value,maturity_date,coupon_rate,payments_per_year,new_discount_rate)[0]
    v_a_r_single_bond = bond_val - new_bond_val
    v_a_r_single_bond_percent = v_a_r_single_bond * 100 / bond_val
    return {'VaR' : v_a_r_single_bond, 'VaR Percentage' : v_a_r_single_bond_percent}

yield_change_matrix = generate_yield_comparison_table_raw ('/Users/baronabramowitz/Desktop/cleaned_corporate_bond_yield_change_data.csv')
yield_change_corr_matrix = yield_change_matrix.corr()
yield_change_cov_matrix = yield_change_matrix.cov()

def value_at_risk_portfolio_set(portfolio_csv_location,loss_percentile):
    portfolio = generate_portfolio(portfolio_csv_location)
    val_portfolio_output = value_portfolio(portfolio_csv_location)
    portfolio_proportions = []
    for bond_val in val_portfolio_output[1]:
        bond_val = bond_val/val_portfolio_output[0]
        portfolio_proportions.append(bond_val)

    print(val_portfolio_output[2])
    maturity_list = []
    for maturity in val_portfolio_output[2]:
        if maturity < 2:
            maturity_list.append(str('2yr_'))
        elif 2 <= maturity <= 3.5:
            maturity_list.append(str('2yr_'))
        elif 3.5 < maturity <= 7.5:
            maturity_list.append(str('5yr_'))
        elif 7.5 < maturity <= 15:
            maturity_list.append(str('10yr_'))
        elif 15 < maturity:
            maturity_list.append(str('20yr_'))
        else:
            print('WTF')
    print(maturity_list)

    loss_percentiles_pre_zip = []
    for item in val_portfolio_output[1]:
        loss_percentiles_pre_zip.append(loss_percentile)

    yield_change_csv_location_pre_zip = []
    for item in val_portfolio_output[1]:
        yield_change_csv_location_pre_zip.append('/Users/baronabramowitz/Desktop/cleaned_corporate_bond_yield_change_data.csv')

    bond_var_portfolio_squared = []
    bond_rating_list = []
    for bond in zip(portfolio['face_value'],portfolio['maturity_date'],portfolio['coupon_rate'],\
                   portfolio['payments_per_year'],portfolio['bond_rating'],portfolio['bond_type'],\
                   yield_change_csv_location_pre_zip,loss_percentiles_pre_zip):
        bond_rating_list.append(bond[4])
        bond_var = value_at_risk_single_bond(*bond)['VaR']
        bond_var_squared = bond_var ** 2
        bond_var_portfolio_squared.append(bond_var_squared)
    bond_rating_maturity = list(map(str.__add__,maturity_list,bond_rating_list))
    print(bond_rating_maturity)
    bond_rating_groupings = list(zip(bond_rating_maturity,portfolio_proportions))
    print(bond_rating_groupings)
    inter_sum_bond_var_squared = sum(bond_var_portfolio_squared)
    portfolio_weights_matrix = pd.DataFrame({'Portfolio_Weights': portfolio_proportions})
    portfolio_cov_matrix_steps = yield_change_cov_matrix
    portfolio_cov_matrix = yield_change_cov_matrix.loc[bond_rating_maturity[0][1][0]]
    print(portfolio_cov_matrix)
    portfolio_variance = np.dot(np.dot(portfolio_weights_matrix.transpose(),portfolio_cov_matrix),portfolio_weights_matrix)
    portfolio_stdev = sqrt(portfolio_variance)
    return portfolio_stdev

class test_suite(unittest.TestCase):
     """Large Selection of Tests for the above code"""
     def test_bond_convexity(self):
         self.assertEqual(35.18162670582754,convexity_bond(10000.0, '2022-06-15', 2.5, 2, 'AAA','Corporate'))
     def test_portfoio_convexity(self):
         self.assertEqual(135.44277212465033,convexity_portfolio('/Users/baronabramowitz/Desktop/bond_portfolio_data.csv'))
     def test_portfolio_duration(self):
         self.assertEqual({'Modified Portfolio Duration': 10.662022505468682,
 'Portfolio Duration': 10.936440783039282},portfolio_duration('/Users/baronabramowitz/Desktop/bond_portfolio_data.csv'))
     def test_value_portfolio(self):
         self.assertEqual((5328131.2278631562,
 [10827.821620777519,
  39873.767697445248,
  3126212.7870177557,
  270005.913906298,
  786543.30874098127,
  353237.85002647078,
  439159.02809525008,
  302270.75075817748]),value_portfolio('/Users/baronabramowitz/Desktop/bond_portfolio_data.csv'))
     def test_bond_dur(self):
        #Checks if bond duration properly calculates
        self.assertEqual({'Bond Duration': 5.4524899454500195, 'Modified Duration': 5.340342747747326},\
            duration_bond(10000.0, '2022-06-15', 2.5, 2, 'AAA','Corporate'))
     def test_bond_val(self):
        #Checks if bond value properly calculates
        self.assertEqual((10398.50651287065,
 [124.23853132907502,
  123.10190870220836,
  121.96952521382494,
  120.853661071975,
  119.72986555876302,
  118.63449141959734,
  117.5491385437076,
  116.47371524943534,
  115.40230284511438,
  114.34652033381887,
  113.29467546037061,
  9092.9121771427599],
 [121, 303, 486, 668, 853, 1035, 1217, 1399, 1582, 1764, 1947, 2129],
 5.832876712328767),\
    value_bond(10000.0, '2022-06-15', 2.5, 2, 'AAA','Corporate'))

if __name__ == "__main__":
    unittest.main()
         

 










