from django.db import models
from django.utils.translation import ugettext_lazy as _
# from numpy import polyfit, poly1d
import numpy as np
import matplotlib.pyplot as plt

"""
Global average usage variables

AvStabilizationTime = {'FSMF': 200000, 'ASIA': 60000}
AvMemoryUsageStabilized = {'FSMF': 1286000, 'ASIA': 2060000}
MaxUsageThreshold = {'FSMF': 0.005, 'ASIA': 0.05}
CriticalUsage = {'FSMF': 1600000, 'ASIA': 2500000}
"""

AvStabilizationTime = 60000 # 12h
AvMemoryUsageStabilized = 2030000 # 2gB
AvDeltaStabilizedTime = 20000 # 12h
DataSamplesMinAmount = 48 # 12h
MaxUsageThreshold = 0.01 # max leak in kB/s
CriticalUsage = 2500000


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
    #trend_start_date = models.DateTimeField(verbose_name=_('trend start date'))
    trend_start_date = models.FloatField(verbose_name=_('trend start date'))
    trend_start_value = models.FloatField(verbose_name=_('trend start value'))
    #trend_end_date = models.DateTimeField(verbose_name=_('trend end date'))
    trend_end_date = models.FloatField(verbose_name=_('trend end date'))
    trend_end_value = models.FloatField(verbose_name=_('trend end value'))

    def __repr__(self):
        return '<{}: #{}>'.format(self.__class__.__name__, self.pk)

    """

    @staticmethod
    def prepare_usage_data(testline_id, data):

        sys_mem_data = []

        """
        latest_smu = SystemMemoryUsage.objects.filter(testline_id=testline_id).latest()
        datetime_cutoff = latest_smu.create_time - timedelta(seconds=latest_smu.uptime) + timedelta(hours=1)
        sys_mem_data = list(SystemMemoryUsage.objects.filter(testline_id=testline_id,
                                                             create_time__gt=datetime_cutoff).values())                                                  
        """

        for elem in data:
            sys_mem_data.append({'uptime': long(elem[0]), 'system': long(elem[1])/1024, 'create_time': long(elem[0])})

        if not sys_mem_data:
            return

        if (sys_mem_data[-1]['uptime'] - sys_mem_data[0]['uptime']) > AvStabilizationTime\
                and len(sys_mem_data) > DataSamplesMinAmount:
            return SystemMemoryUsageTrend.return_usage_data(sys_mem_data)
        else:
            print 'Too low amount of usage data'
            return

    @staticmethod
    def return_usage_data(sys_mem_data):

        uptime_data = []
        system_data = []

        for element in sys_mem_data:
            uptime_data.append(element['uptime'])
            system_data.append(element['system'])


        """***************
        # smooth data by moving average box algorithm
        **************"""

        system_smooth = SystemMemoryUsageTrend.average_box_smooth(system_data, 1)
        #uptime_data = uptime_data[1:]
        #system_data = system_data[1:]

        plt.plot(uptime_data, system_smooth, 'y.')
        plt.plot(uptime_data, system_data, 'b.')

        """***************
        #check if local minimum is visible
        **************"""
        poly = np.polyfit(uptime_data, system_smooth,6)
        aprox = np.poly1d(poly)
        system_smooth_approx = []

        for i in uptime_data:
            system_smooth_approx.append(aprox(i))

        gradients = np.diff(system_smooth_approx)

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

        plt.plot(uptime_data, system_smooth_approx, 'r.')

        for i in turning_points['minima_locations']:
            plt.plot(uptime_data[i], system_smooth_approx[i], 'bo')

        for i in turning_points['maxima_locations']:
            plt.plot(uptime_data[i], system_smooth_approx[i], 'go')


        """***************
        if 1 local minimum found:
            prepare stabilized data
        elif >2 local minimum found:
        
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
        else:
            prepare unstabilized data (only to fill trend model)
        **************"""
        if turning_points['minima_locations']:

            print 'local min found'
            stabilization_start_time = turning_points['minima_locations'][0]
            uptime_stabilized = uptime_data[stabilization_start_time:]
            system_smooth_stabilized = system_smooth[stabilization_start_time:]
            plt.plot(uptime_stabilized, system_smooth_stabilized, 'y.')

            usage_trend_data = SystemMemoryUsageTrend.return_usage_trend_data(uptime_stabilized, system_smooth_stabilized,
                                                                           stabilization_start_time)

            XDATA = [usage_trend_data['trend_start_uptime'], usage_trend_data['trend_end_uptime']]
            YDATA = [usage_trend_data['trend_start_value'], usage_trend_data['trend_end_value']]
            plt.plot(XDATA,YDATA, color='black', marker='+')

        else:
            print 'local min not found'
            stabilization_start_time = None
            usage_trend_data = SystemMemoryUsageTrend.return_usage_trend_data(uptime_data, system_smooth,
                                                                           stabilization_start_time)

            plt.plot(usage_trend_data['trend_start_uptime'], usage_trend_data['trend_start_value'], color='black',
                     marker='^')
            plt.plot(usage_trend_data['trend_end_uptime'], usage_trend_data['trend_end_value'], color='black',
                     marker='^')
        plt.show()

        print usage_trend_data

        return usage_trend_data

    @staticmethod
    def return_usage_trend_data(uptime, system_smooth, stabilization_start_time):
        """***************
        Prepare last set of stabilized usage data (deltaKb + deltaUptime)
        **************"""
        if stabilization_start_time:
            is_stabilized_trend_data = True
        else:
            is_stabilized_trend_data = False

        a, b = np.polyfit(uptime, system_smooth, 1)

        trend_start_value = a * uptime[0] + b
        trend_end_value = a * uptime[-1] + b

        trend_leak_value = (trend_end_value-trend_start_value)/(uptime[-1]-uptime[0])

        # added 'trend_leak_value'
        # added 'is_stabilized_trend_data'
        usage_trend_data = {
            'trend_start_uptime': uptime[0],
            'trend_start_value': trend_start_value,
            'trend_end_uptime': uptime[-1],
            'trend_end_value': trend_end_value,
            'trend_leak_value': trend_leak_value,
            'is_stabilized_trend_data': is_stabilized_trend_data
        }
        return usage_trend_data

    @staticmethod
    def average_box_smooth(y, box_pts):
        box = np.ones(box_pts) / box_pts
        y_smooth = np.convolve(y, box, mode='same')
        return y_smooth

    def has_memory_leak_stable_data(self, data, testline_id):

        """
        TO DO:
        divide HW types [ASIA, FSMF)
        """
        time_delta = data['trend_end_uptime'] - data['trend_start_uptime']
        print 'usage {} >< AvMemoryUsageStabilized {}'.format(data['trend_end_value'], AvMemoryUsageStabilized)
        print 'time_delta {} >< AvStabilizationTime {}'.format(time_delta, AvStabilizationTime)
        print "data['trend_leak_value'] {} >< USAGE_THRESHOLD {}".format(data['trend_leak_value'], MaxUsageThreshold)

        if data['trend_leak_value'] > MaxUsageThreshold and time_delta > AvDeltaStabilizedTime:
            if data['trend_end_value'] > AvMemoryUsageStabilized:
                return 'Memory_Leak'
            else:
                return "Possible_Memory_Leak"
        else:
            return None

    def has_memory_leak_unstable_data(self, data, testline_id):

        """
         TO DO:
         divide HW types [ASIA, FSMF)
         """
        time_delta = data['trend_end_uptime'] - data['trend_start_uptime']
        print 'usage {} > AvMemoryUsageStabilized {}'.format(data['trend_end_value'], AvMemoryUsageStabilized)
        print 'time_delta {} > AvStabilizationTime {}'.format(time_delta, AvStabilizationTime)

        if data['trend_end_value'] > AvMemoryUsageStabilized and time_delta > AvStabilizationTime:
            if data['trend_end_value'] > CriticalUsage:
                return 'Memory_Leak'
            else:
                return 'Possible_Memory_Leak'

        else:
            return None
