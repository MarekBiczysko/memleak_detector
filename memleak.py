from datetime import timedelta
from math import atan, degrees
from django.db import models
from django.utils.translation import ugettext_lazy as _
from numpy import polyfit, poly1d
import csv
import matplotlib.pyplot as plt


USAGE_THRESHOLD = 15
testline_id = 666



"""
class BaseUsage(models.Model):
    create_time = models.DateTimeField(verbose_name=_('create time'))

    class Meta:
        abstract = True


class SystemMemoryUsage(BaseUsage):
    testline_id = 666

    testline = models.ForeignKey('scout.TestLine', on_delete=models.CASCADE, related_name='system_memory_usages',
                                 verbose_name=_('testline'))
    uptime = models.BigIntegerField(verbose_name=_('uptime'))
    system = models.BigIntegerField(verbose_name=_('system'))
    ram = models.BigIntegerField(verbose_name=_('ram'))
    rom = models.BigIntegerField(verbose_name=_('rom'))
    rpram = models.BigIntegerField(verbose_name=_('rpram'))
    slab = models.BigIntegerField(verbose_name=_('slab'))

    def __unicode__(self):
        return '{} {} uptime:{} system:{} ram:{} rom:{} rpram:{} slab:{}'.format(

            self.create_time, self.testline_id, self.uptime, self.system, self.ram, self.rom, self.rpram, self.slab
        )

    def __repr__(self):
        return '<{}: #{}>'.format(self.__class__.__name__, self.pk)

    @staticmethod
    def get_cache_key(testline):
        return 'system_memory_{}'.format(testline)

    class Meta:
        verbose_name = _('system memory usage')
        verbose_name_plural = _('system memory usages')
        unique_together = ('testline', 'create_time')
        get_latest_by = 'create_time'
        ordering = ('create_time',)
"""

# class SystemMemoryUsageTrend(models.Model):
class SystemMemoryUsageTrend():

    """
    testline = models.OneToOneField('scout.TestLine', on_delete=models.CASCADE, primary_key=True,
                                    related_name='system_memory_usage_trend', verbose_name=_('testline'))
    trend_start_date = models.DateTimeField(verbose_name=_('trend start date'))
    trend_start_value = models.FloatField(verbose_name=_('trend start value'))
    trend_end_date = models.DateTimeField(verbose_name=_('trend end date'))
    trend_end_value = models.FloatField(verbose_name=_('trend end value'))

    def __repr__(self):
        return '<{}: #{}>'.format(self.__class__.__name__, self.pk)

    """

    @staticmethod
    def calculate_trend(testline_id, data_filename):
        uptime = []
        system = []
        sys_mem_data = []

        """
        latest_smu = SystemMemoryUsage.objects.filter(testline_id=testline_id).latest()
        datetime_cutoff = latest_smu.create_time - timedelta(seconds=latest_smu.uptime) + timedelta(hours=1)
        sys_mem_data = list(SystemMemoryUsage.objects.filter(testline_id=testline_id,
                                                             create_time__gt=datetime_cutoff).values())                                                  
        """


        #WCZYTYWANIE Z PLIKU DO SYS_MEM)DATA
        with open(data_filename, 'rb') as f:
            reader = csv.reader(f)
            sys_mem_data_list = list(reader)


        # system imported in kB !!!!!!!!!!!!!!!!!!!!!!!
        for elem in sys_mem_data_list:
            sys_mem_data.append({'uptime': int(float(elem[0])), 'system': float(elem[1])/1000, 'create_time': int(float(elem[0]))})


        trend_start_date = sys_mem_data[0]['uptime']
        trend_end_date = sys_mem_data[-1]['uptime']

        if not sys_mem_data:
            return

        for element in sys_mem_data:
            uptime.append(element['uptime'])
            system.append(element['system'])



        a, b = polyfit(uptime, system, 1)

        trend_start_value = a * sys_mem_data[0]['uptime'] + b
        trend_end_value = a * sys_mem_data[-1]['uptime'] + b

        data = {
            'trend_start_date': sys_mem_data[0]['create_time'],
            'trend_start_value': trend_start_value,
            'trend_end_date': sys_mem_data[-1]['create_time'],
            'trend_end_value': trend_end_value
        }

        return data, uptime, system


    def has_memory_leak(self, data):
        # time_delta_seconds = (data['trend_end_date'] - data['trend_start_date']).total_seconds()
        time_delta_seconds = (data['trend_end_date'] - data['trend_start_date'])

        print 'TIMEDELTASECONDS', time_delta_seconds

        tangens_alfa = (data['trend_end_value'] - data['trend_start_value']) / time_delta_seconds

        print 'valuedelta', (data['trend_end_value'] - data['trend_start_value'])

        print 'tangens alfa', tangens_alfa

        alfa_deg = degrees(atan(tangens_alfa))

        print '@DEG:', alfa_deg

        return alfa_deg > USAGE_THRESHOLD

    def PlotChart(self, uptime, system, data):

        a, b = polyfit(uptime, system, 1)
        poly5 = polyfit(uptime, system, 5)
        multi5 = poly1d(poly5)
        poly4 = polyfit(uptime, system, 4)
        multi4 = poly1d(poly4)
        poly3 = polyfit(uptime, system, 3)
        multi3 = poly1d(poly3)
        poly2 = polyfit(uptime, system, 2)
        multi2 = poly1d(poly2)


        for i in uptime[::10]:
            plt.plot(i, i * a + b, 'g.')
            UptimeIndex = uptime.index(i)
            plt.plot(i, system[UptimeIndex], 'b*')
            plt.plot(i, multi5(i), 'r+')
            plt.plot(i, multi4(i), 'y+')

        plt.show()









data_filename = 'data_long_stable.csv'
#data_filename = 'data_long_stable_leak.csv'
#data_filename = 'data_short_stable.csv'
#data_filename = 'data_short_stable_leak.csv'

Leak = SystemMemoryUsageTrend()
data, uptime, system = Leak.calculate_trend(testline_id, data_filename)
print Leak.has_memory_leak(data)

Leak.PlotChart(uptime, system, data)