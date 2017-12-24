from datetime import timedelta
from math import atan, degrees
from django.db import models
from django.utils.translation import ugettext_lazy as _
# from numpy import polyfit, poly1d
import numpy as np
import csv
import matplotlib.pyplot as plt


USAGE_THRESHOLD = 1
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


        """***************
        Load data test cases
        **************"""
        uptime = []
        system = []
        sys_mem_data = []

        """
        latest_smu = SystemMemoryUsage.objects.filter(testline_id=testline_id).latest()
        datetime_cutoff = latest_smu.create_time - timedelta(seconds=latest_smu.uptime) + timedelta(hours=1)
        sys_mem_data = list(SystemMemoryUsage.objects.filter(testline_id=testline_id,
                                                             create_time__gt=datetime_cutoff).values())                                                  
        """

        with open(data_filename, 'rb') as f:
            reader = csv.reader(f)
            sys_mem_data_list = list(reader)


        # convert usage to kB
        for elem in sys_mem_data_list:
            sys_mem_data.append({'uptime': int(float(elem[0])), 'system': float(elem[1])/1000, 'create_time': int(float(elem[0]))})


        #trend_start_date = sys_mem_data[0]['create_time']
        #trend_end_date = sys_mem_data[-1]['create_time']

        if not sys_mem_data:
            return

        """***************
        # prepare 'uptime' and 'system' lists
        **************"""


        for element in sys_mem_data:
            uptime.append(element['uptime'])
            system.append(element['system'])


        """***************
        # smooth data by moving average box algorithm
        **************"""

        system_smooth = SystemMemoryUsageTrend.AverageBoxSmooth(system, 3)
        uptime = uptime[1:]
        system = system[1:]

        plt.plot(uptime, system, 'b.')

        """***************
        #check if local minimum is visible
        **************"""

        poly = np.polyfit(uptime, system_smooth, 6)
        aprox = np.poly1d(poly)
        system_smooth_approx = []

        for i in uptime:
            system_smooth_approx.append(aprox(i))

        gradients = np.diff(system_smooth_approx)

        print '***************************'
        maxima_num = 0
        minima_num = 0
        max_locations = []
        min_locations = []
        count = 0
        for i in gradients[:-1]:
            count += 1
            if ((cmp(i, 0) > 0) & (cmp(gradients[count], 0) < 0) & (i != gradients[count])):
                maxima_num += 1
                max_locations.append(count)

            if ((cmp(i, 0) < 0) & (cmp(gradients[count], 0) > 0) & (i != gradients[count])):
                minima_num += 1
                min_locations.append(count)

        turning_points = {'maxima_number': maxima_num, 'minima_number': minima_num, 'maxima_locations': max_locations,
                          'minima_locations': min_locations}

        print turning_points
        print '***************************'

        plt.plot(uptime, system_smooth_approx, 'r.')

        for i in turning_points['minima_locations']:
            print '%%%%%', uptime[i], system_smooth_approx[i]
            plt.plot(uptime[i], system_smooth_approx[i], 'bo')

        for i in turning_points['maxima_locations']:
            print '$$$$$', uptime[i], system_smooth_approx[i]
            plt.plot(uptime[i], system_smooth_approx[i], 'go')


        """***************
        #If 1st local minimum found- prepare stabilized data
        **************"""
        if turning_points['minima_locations']:
            Tstab = turning_points['minima_locations'][0]
            uptime_stab = uptime[Tstab:-1]
            system_smooth_stab = system_smooth[Tstab:-1]
            plt.plot(uptime_stab, system_smooth_stab, 'y.')

            stabilized_data = SystemMemoryUsageTrend.returnStabilizedUsageData(uptime_stab, system_smooth_stab, sys_mem_data, Tstab)

            print 'Stablizeddata', stabilized_data
            plt.plot(stabilized_data['trend_start_date'], stabilized_data['trend_start_value'], color='darkgreen', marker='^')
            plt.plot(stabilized_data['trend_start_date'], stabilized_data['trend_start_value'], color='darkgreen', marker='^')


        plt.show()

        return stabilized_data, uptime, system, system_smooth, turning_points['minima_locations']



    """***************
           def returnStabilizedUsageData(uptime_stab, system_smooth_stab, sys_mem_data, Tstab):
           Return stabilized trend values ; data
    **************"""

    @staticmethod
    def returnStabilizedUsageData(uptime_stab, system_smooth_stab, sys_mem_data, Tstab):
        """***************
        Prepare last set of stabilized usage data (deltaKb + deltaUptime)
        **************"""

        a, b = np.polyfit(uptime_stab, system_smooth_stab, 1)

        trend_start_value = a * uptime_stab[0] + b
        trend_end_value = a * uptime_stab[-1] + b

        data = {
            'trend_start_date': sys_mem_data[Tstab]['create_time'],
            'trend_start_value': trend_start_value,
            'trend_end_date': sys_mem_data[-1]['create_time'],
            'trend_end_value': trend_end_value
        }
        return data


    @staticmethod
    def AverageBoxSmooth(y, box_pts):
        box = np.ones(box_pts) / box_pts
        y_smooth = np.convolve(y, box, mode='same')
        return y_smooth[1:]


    def has_memory_leak(self, data):


        """
        tutaj wchodzi teoretycznie ustabilizowany kawalek danych
        a tak naprawde ilosc danych ktore uciekly w kb i czas w ktorym to nastapilo
        porownywane jest to z parametrami sprzetowymi
        na yjsciu moga byc wartosci Stab_time, possible_leak, leak!
        :param data:
        :return:
        """
        # time_delta_seconds = (data['trend_end_date'] - data['trend_start_date']).total_seconds()
        time_delta_seconds = (data['trend_end_date'] - data['trend_start_date'])

        print 'TIMEDELTASECONDS', time_delta_seconds

        tangens_alfa = (data['trend_end_value'] - data['trend_start_value']) / time_delta_seconds

        print 'valuedelta', (data['trend_end_value'] - data['trend_start_value'])

        print 'tangens alfa', tangens_alfa

        alfa_deg = degrees(atan(tangens_alfa))

        print '@DEG:', alfa_deg

        return alfa_deg > USAGE_THRESHOLD



#data_filename = 'data_long_stable.csv'
#data_filename = 'data_long_stable_leak.csv'
#data_filename = 'data_short_stable.csv'
data_filename = 'data_short_stable_leak.csv'

Leak = SystemMemoryUsageTrend()
data, uptime, system, system_smooth, minimas = Leak.calculate_trend(testline_id, data_filename)
print Leak.has_memory_leak(data)
