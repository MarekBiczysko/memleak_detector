from memleak4 import SystemMemoryUsageTrend
import csv

testline_id = 666

def returnLinesFromDataFile(data_filename, percentOfData):

    with open(data_filename, 'rb') as f:
        reader = csv.reader(f)
        full_data = list(reader)
        sliceDataEnd = int(percentOfData/100*len(full_data))
        sliceData = full_data[:sliceDataEnd]
        return sliceData


#def _update_system_memory_usage_trend(self, testline_id, data):
def _update_system_memory_usage_trend(testline_id, data):
    """
    if not models.SystemMemoryUsage.objects.filter(testline_id=testline_id).exists():
        return
    """

    # sys_mem_trend = models.SystemMemoryUsageTrend.calculate_trend(testline_id)
    sys_mem_trend = SystemMemoryUsageTrend.prepare_usage_data(testline_id, data)
    if not sys_mem_trend:
        return

    #local solution:
    UsageObject = SystemMemoryUsageTrend()
    trend = sys_mem_trend
    # trend = self._update_or_create(models.SystemMemoryUsageTrend, sys_mem_trend[0], testline_id=testline_id)


    """
    try:
        obj = self.get_object(testline_id)
    except self.model.DoesNotExist:
        logger.exception('{} not found!'.format(self.model), extra={
            'data': {
                'pk': testline_id,
            }
        })
        return
    """

    #trend[0] - data trend from [-2] local min to the end
    #trend[1] - last two local mins trend
    #trend[2] - last two local maxs trend
    if len(trend) > 1:
        #leak_type = trend.has_memory_leak_stable_data()
        #local solution:
        leak_type = UsageObject.has_memory_leak_stable_data(trend, testline_id)
        if leak_type:
            # models.ScoutAlarm.create_if_not_exists(obj, 'memory')   - original
            # models.ScoutAlarm.create_if_not_exists(obj, leak_type)  # memory_leak; possible_memory_leak
            print 'raise memory leak alarm!!: {}'.format(leak_type)
            print '____________________________________________________________'
        else:
            #models.ScoutAlarm.cancel(obj, 'memory')
            print 'cancel memory leak alarm!!'
            print '____________________________________________________________'
    else:
        #leak_type = trend.has_memory_leak_unstable_data()
        # local solution:
        leak_type = UsageObject.has_memory_leak_unstable_data(trend[0], testline_id)
        if leak_type:
            #models.ScoutAlarm.create_if_not_exists(obj, leak_type)  # memory_leak; possible_memory_leak
            print 'raise memory leak alarm!!: {}'.format(leak_type)
            print '____________________________________________________________'
        else:
            #models.ScoutAlarm.cancel(obj, 'memory')
            print 'cancel memory leak alarm!!'
        print '____________________________________________________________'


#data_filename = 'data_long_stable.csv'
#data_filename = 'data_short_stable_mini_leak.csv'
data_filename = 'MRBTS-101045MRBTS.csv'
#data_filename = 'MRBTS-101048MRBTS.csv'


for i in [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0, 80.0, 90.0, 100.0]:
    print '{}% of entry data'.format(i)
    data = returnLinesFromDataFile(data_filename, i)
    _update_system_memory_usage_trend(testline_id, data)