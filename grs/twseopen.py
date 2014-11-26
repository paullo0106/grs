# -*- coding: utf-8 -*-
''' TWSE open date '''
# Copyright (c) 2012, 2013, 2014 Toomore Chiang, http://toomore.net/
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from .tw_time import TWTime
from datetime import datetime
from datetime import timedelta
import csv
import os


class TWSEOpen(object):
    ''' 判斷當日是否開市 '''
    def __init__(self):
        ''' 載入相關檔案 '''
        self.__ocdate = self.__loaddate()
        self.twtime = ''

    def d_day(self, time):
        ''' 指定日期

            :param datetime time: 欲判斷的日期
            :rtype: bool
            :returns: True 為開市、False 為休市
        '''
        if type(time) == type(TWTime().now):
            self.twtime = TWTime().now
        elif type(time) == type(TWTime().date):
            self.twtime = TWTime().date
        else:
            pass
        return self.caldata(time)

    def recent_open_day(self, latest_open, backward_check=True):
        ''' 尋找離指定日期(包含當天)最近一天有開市的日期

            :param datetime latest_open: 指定日期
            :param boolean backward_check: True (default) - 從指定日期往前查找, False - 往後查找
            :rtype: datetime
            :returns: 離指定日期最近一天有開市的日期
        '''
        diff = -1 if backward_check else 1
        is_open = self.d_day(latest_open)
        while not is_open:  # continue moving the clock one day backward/forward to check
            latest_open = latest_open + timedelta(days=diff)
            is_open = self.d_day(latest_open)
        return latest_open

    @staticmethod
    def __loaddate():
        ''' 載入檔案
            檔案依據 http://www.twse.com.tw/ch/trading/trading_days.php
        '''
        csv_path = os.path.join(os.path.dirname(__file__), 'opendate.csv')
        with open(csv_path) as csv_file:
            csv_data = csv.reader(csv_file)
            result = {}
            result['close'] = []
            result['open'] = []
            for i in csv_data:
                if i[1] == '0':  # 0 = 休市
                    result['close'].append(datetime.strptime(i[0],
                                                             '%Y/%m/%d').date())
                elif i[1] == '1':  # 1 = 開市
                    result['open'].append(datetime.strptime(i[0],
                                                            '%Y/%m/%d').date())
                else:
                    pass
            return result

    def caldata(self, time):
        ''' Market open or not.

            :param datetime time: 欲判斷的日期
            :rtype: bool
            :returns: True 為開市、False 為休市
        '''
        if time.date() in self.__ocdate['close']:  # 判對是否為法定休市
            return False
        elif time.date() in self.__ocdate['open']:  # 判對是否為法定開市
            return True
        else:
            if time.weekday() <= 4:  # 判斷是否為平常日開市
                return True
            else:
                return False
