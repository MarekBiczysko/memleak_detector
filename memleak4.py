from django.db import models
from django.utils.translation import ugettext_lazy as _
# from numpy import polyfit, poly1d
from numpy import polyfit, poly1d, diff, ones, convolve
import matplotlib.pyplot as plt

"""
Global average usage variables

AvStabilizationTime = {'FSMF': 200000, 'ASIA': 60000}
MaxUsageThreshold = {'FSMF': 0.005, 'ASIA': 0.05}
CriticalUsage = {'FSMF': 1600000, 'ASIA': 2500000}
"""

AvStabilizationTime = 60000 # 12h
AvDeltaStabilizedTime = 50000 # 12h
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
        create_time_data = []

        for element in sys_mem_data:
            uptime_data.append(element['uptime'])
            system_data.append(element['system'])
            create_time_data.append(element['create_time'])


        """***************
        # smooth data by moving average box algorithm
        **************"""

        system_smooth = SystemMemoryUsageTrend.average_box_smooth(system_data, 1)

        plt.plot(uptime_data, system_smooth, 'y.')

        """***************
        #check if local minimum is visible
        **************"""
        poly = polyfit(uptime_data, system_smooth,8)
        aprox = poly1d(poly)
        system_smooth_approx = []

        for i in uptime_data:
            system_smooth_approx.append(aprox(i))

        gradients = diff(system_smooth_approx)

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


        """
        Analysis based on turning points
        """

        usage_trend_data = SystemMemoryUsageTrend.data_mono_analysis(turning_points, uptime_data, system_smooth, create_time_data)

        print usage_trend_data

        return usage_trend_data

    @staticmethod
    def data_mono_analysis(turning_points, uptime_data, system_data, create_time_data):

        """***************
        If no_of_local_min/max >= 2:
            data is stabilized
        else:
            data is not stabilized
        **************"""

        trends_data = []

        NoOfLocalMins = len(turning_points['minima_locations'])
        NoOfLocalMax = len(turning_points['maxima_locations'])

        if NoOfLocalMins == 1:

            print '{} local mins found'. format(NoOfLocalMins)
            stabilization_start_time = turning_points['minima_locations'][0]
            uptime_stabilized = uptime_data[stabilization_start_time:]
            system_stabilized = system_data[stabilization_start_time:]
            create_time_stabilized = create_time_data[stabilization_start_time:]
            plt.plot(uptime_stabilized, system_stabilized, 'y.')

            usage_trend_data = SystemMemoryUsageTrend.return_usage_trend_data(uptime_stabilized, system_stabilized, create_time_stabilized)
            trends_data.append(usage_trend_data)

            XDATA = [usage_trend_data['trend_start_uptime'], usage_trend_data['trend_end_uptime']]
            YDATA = [usage_trend_data['trend_start_value'], usage_trend_data['trend_end_value']]
            plt.plot(XDATA, YDATA, color='black', marker='s')

        elif NoOfLocalMins >= 2 and NoOfLocalMax >= 2:

            print '{} local mins found'.format(NoOfLocalMins)
            print '{} local maxs found'.format(NoOfLocalMax)

            stabilization_start_time_min = turning_points['minima_locations'][-2]
            stabilization_end_time_min = turning_points['minima_locations'][-1]

            stabilization_start_time_max = turning_points['maxima_locations'][-2]
            stabilization_end_time_max = turning_points['maxima_locations'][-1]

            stabilization_start_time = turning_points['minima_locations'][-2]

            uptime_stabilized_min = uptime_data[stabilization_start_time_min:stabilization_end_time_min]
            system_stabilized_min = system_data[stabilization_start_time_min:stabilization_end_time_min]
            create_time_stabilized_min = create_time_data[stabilization_start_time::stabilization_end_time_min]

            uptime_stabilized_max = uptime_data[stabilization_start_time_max:stabilization_end_time_max]
            system_stabilized_max = system_data[stabilization_start_time_max:stabilization_end_time_max]
            create_time_stabilized_max = create_time_data[stabilization_start_time::stabilization_end_time_max]

            uptime_stabilized = uptime_data[stabilization_start_time:]
            system_stabilized = system_data[stabilization_start_time:]
            create_time_stabilized = create_time_data[stabilization_start_time:]

            usage_trend_data_min = SystemMemoryUsageTrend.return_usage_trend_data(uptime_stabilized_min,
                                                                                  system_stabilized_min,
                                                                                  create_time_stabilized_min)

            usage_trend_data_max = SystemMemoryUsageTrend.return_usage_trend_data(uptime_stabilized_max,
                                                                                  system_stabilized_max,
                                                                                  create_time_stabilized_max)

            usage_trend_data = SystemMemoryUsageTrend.return_usage_trend_data(uptime_stabilized,
                                                                              system_stabilized,
                                                                              create_time_stabilized)

            trends_data.append(usage_trend_data)
            trends_data.append(usage_trend_data_min)
            trends_data.append(usage_trend_data_max)

            XDATA = [usage_trend_data['trend_start_uptime'], usage_trend_data['trend_end_uptime']]
            YDATA = [usage_trend_data['trend_start_value'], usage_trend_data['trend_end_value']]

            XDATA_min = [usage_trend_data_min['trend_start_uptime'], usage_trend_data_min['trend_end_uptime']]
            YDATA_min = [usage_trend_data_min['trend_start_value'], usage_trend_data_min['trend_end_value']]

            XDATA_max = [usage_trend_data_max['trend_start_uptime'], usage_trend_data_max['trend_end_uptime']]
            YDATA_max = [usage_trend_data_max['trend_start_value'], usage_trend_data_max['trend_end_value']]

            plt.plot(XDATA_min, YDATA_min, color='blue', marker='D')
            plt.plot(XDATA_max, YDATA_max, color='green', marker='H')
            plt.plot(XDATA, YDATA, color='black', marker='X')

        else:
            print 'local min not found'
            usage_trend_data = SystemMemoryUsageTrend.return_usage_trend_data(uptime_data, system_data, create_time_data)

            trends_data.append(usage_trend_data)

            plt.plot(usage_trend_data['trend_start_uptime'], usage_trend_data['trend_start_value'], color='black',
                     marker='^')
            plt.plot(usage_trend_data['trend_end_uptime'], usage_trend_data['trend_end_value'], color='black',
                     marker='^')
        plt.show()

        return trends_data




    @staticmethod
    def return_usage_trend_data(uptime, system, create_time):
        """***************
        Prepare last set of stabilized usage data (deltaKb + deltaUptime)
        **************"""

        a, b = polyfit(uptime, system, 1)

        trend_start_value = a * uptime[0] + b
        trend_end_value = a * uptime[-1] + b

        trend_leak_value = (trend_end_value-trend_start_value)/(uptime[-1]-uptime[0])

        # added 'trend_leak_value'
        # added 'is_stabilized_trend_data'
        usage_trend_data = {
            'trend_start_uptime': uptime[0],
            'trend_start_value': trend_start_value,
            'trend_start_date': create_time[0],
            'trend_end_uptime': uptime[-1],
            'trend_end_value': trend_end_value,
            'trend_end_date': create_time[-1],
            'trend_leak_value': trend_leak_value,
        }
        return usage_trend_data

    @staticmethod
    def average_box_smooth(y, box_pts):
        box = ones(box_pts) / box_pts
        y_smooth = convolve(y, box, mode='same')
        return y_smooth

    def has_memory_leak_stable_data(self, data, testline_id):

        """
        TO DO:
        divide HW types [ASIA, FSMF)
        """

        # data[0] - data trend from [-2] local min to the end
        # data[1] - last two local mins trend
        # data[2] - last two local maxs trend

        time_delta = data[0]['trend_end_uptime'] - data[0]['trend_start_uptime']
        print 'usage: {}'.format(data[0]['trend_end_value'])
        print 'time_delta: {} >< AvStabilizationTime: {}'.format(time_delta, AvStabilizationTime)
        print "data['trend_leak_value'] {} >< USAGE_THRESHOLD {}".format(data[0]['trend_leak_value'], MaxUsageThreshold)
        print "data_min['trend_leak_value'] {} >< USAGE_THRESHOLD {}".format(data[1]['trend_leak_value'], MaxUsageThreshold)
        print "data_max['trend_leak_value'] {} >< USAGE_THRESHOLD {}".format(data[2]['trend_leak_value'], MaxUsageThreshold)

        if data[0]['trend_leak_value'] > MaxUsageThreshold:
            if time_delta > AvDeltaStabilizedTime and data[1]['trend_leak_value'] > MaxUsageThreshold\
                    and data[2]['trend_leak_value'] > MaxUsageThreshold:
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
        print 'usage: {}'.format(data['trend_end_value'])
        print 'time_delta {} > AvStabilizationTime {}'.format(time_delta, AvStabilizationTime)
        print "data['trend_leak_value'] {} >< USAGE_THRESHOLD {}".format(data['trend_leak_value'], MaxUsageThreshold)

        if data['trend_leak_value'] > MaxUsageThreshold and time_delta > AvStabilizationTime:
            if data['trend_end_value'] > CriticalUsage:
                return 'Memory_Leak'
            else:
                return 'Possible_Memory_Leak'

        else:
            return None
