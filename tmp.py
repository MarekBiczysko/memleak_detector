import numpy as np

"""
x = np.linspace(0, 2 * np.pi, 100)
y = np.sin(x) + np.random.random(100) * 0.8


print x

print '&&&'

print y



class SystemMemoryUsageTrend():

    @staticmethod
    def calc(x):
        return x


    def calculate_trend(testline_id, data_filename):
        print 'aaa'

        SystemMemoryUsageTrend.calc()


print range(10)
"""


USAGE_CRITICAL_USAGE_VALUE = {
    'FSMF': {
        'System Usage': 0.001,
        'HWRClockSExe': 0.0001,
        'HWRTrblSExe': 0.0001,
        'BTSOMexe': 0.0001,
        'LOMexe': 0.0001,
        'CEM': 0.0001,
        'MCI': 0.0001,
        'FRI': 0.0001,
        'dtfs': 0.0001,
        'HWRStartupExe': 0.0001,
        'TUPcexe': 0.0001,
        'rsyslogd': 0.0001,
        'HWRTopSExe': 0.0001,
        'HWRIstiSExe': 0.0001,
        'InfoModelGwExe': 0.0001,
        'systemd-journal': 0.0001,
        'FaultServiceEx': 0.0001,
        'FjCpri': 0.0001,
        'HWRAdetMasterE': 0.0001,
        'HAS': 0.0001,
        'HWRPostSExe': 0.0001,
        'BBCUTILexe': 0.0001,
        'HWRSfpSExe': 0.0001,
        'HWRCpriSExe': 0.0001,
        'HWRSumSExe': 0.0001,
        'CELLCexe': 0.0001,
        'HWRSupervisor': 0.0001,
        'WRRoutingSExe': 0.0001,
        'SysAdapter': 0.0001,
        'ipcsAdaptor': 0.0001,
        'trsDrvCore': 0.0001,
        'HWRBasebandSEx': 0.0001,
        'DCS': 0.0001,
        'HWRSwDlSExe': 0.0001,
        'HWRBlackboxSEx': 0.0001,
        'RROMexe': 0.0001,
        'HWRResetSExe': 0.0001,
        'bm': 0.0001,
        'UECexe': 0.0001,
        'trsMgr': 0.0001,
        'HWRLedSExe': 0.0001,
        'systemd': 0.0001,
        'HWRAdetSlaveEx': 0.0001,
        'HWRTimeSExe': 0.0001,
        'fpb': 0.0001,
        'MCECexe': 0.0001,
        'HWRIpSExe': 0.0001,
        'MCtrl': 0.0001,
        'gpsd': 0.0001,
        'REM': 0.0001,
        'Nma': 0.0001,
        'HWRRatSupervis': 0.0001,
        'HWRSrioSExe': 0.0001,
        'CCS': 0.0001,
        'DEM': 0.0001,
        'dhcpd': 0.0001,
        'BStat': 0.0001,
        'SmaFileTransfer': 0.0001,
        'HWRBbTraceSExe': 0.0001,
        'HWRClimateSExe': 0.0001,
        'HWRAlarmSExe': 0.0001,
        'HWRGnssSExe': 0.0001,
        'HWREacSExe': 0.0001,
        'SWM': 0.0001,
        'SmaAsn1': 0.0001,
        'HWRRoutingSExe': 0.0001,
        'HWRMurkkuLogge': 0.0001,
        'ENBCexe': 0.0001,
        'HWRAdetSExe': 0.0001,
        'SmaCertMgr': 0.0001,
        'SmaRuim': 0.0001
    },
    'ASIA': {
        'System Usage': 2500,
        'HWRClockSExe': 10,
        'HWRTrblSExe': 5,
        'BTSOMexe': 50,
        'LOMexe': 5,
        'CEM': 10,
        'MCI': 10,
        'FRI': 20,
        'dtfs': 20,
        'HWRStartupExe': 5,
        'TUPcexe': 20,
        'rsyslogd': 0.0001,
        'HWRTopSExe': 0.0001,
        'HWRIstiSExe': 0.0001,
        'InfoModelGwExe': 0.0001,
        'systemd-journal': 0.0001,
        'FaultServiceEx': 0.0001,
        'FjCpri': 0.0001,
        'HWRAdetMasterE': 0.0001,
        'HAS': 0.0001,
        'HWRPostSExe': 0.0001,
        'BBCUTILexe': 0.0001,
        'HWRSfpSExe': 0.0001,
        'HWRCpriSExe': 0.0001,
        'HWRSumSExe': 0.0001,
        'CELLCexe': 0.0001,
        'HWRSupervisor': 0.0001,
        'WRRoutingSExe': 0.0001,
        'SysAdapter': 0.0001,
        'ipcsAdaptor': 0.0001,
        'trsDrvCore': 0.0001,
        'HWRBasebandSEx': 0.0001,
        'DCS': 0.0001,
        'HWRSwDlSExe': 0.0001,
        'HWRBlackboxSEx': 0.0001,
        'RROMexe': 0.0001,
        'HWRResetSExe': 0.0001,
        'bm': 0.0001,
        'UECexe': 0.0001,
        'trsMgr': 0.0001,
        'HWRLedSExe': 0.0001,
        'systemd': 0.0001,
        'HWRAdetSlaveEx': 0.0001,
        'HWRTimeSExe': 0.0001,
        'fpb': 0.0001,
        'MCECexe': 0.0001,
        'HWRIpSExe': 0.0001,
        'MCtrl': 0.0001,
        'gpsd': 0.0001,
        'REM': 0.0001,
        'Nma': 0.0001,
        'HWRRatSupervis': 0.0001,
        'HWRSrioSExe': 0.0001,
        'CCS': 0.0001,
        'DEM': 0.0001,
        'dhcpd': 0.0001,
        'BStat': 0.0001,
        'SmaFileTransfer': 0.0001,
        'HWRBbTraceSExe': 0.0001,
        'HWRClimateSExe': 0.0001,
        'HWRAlarmSExe': 0.0001,
        'HWRGnssSExe': 0.0001,
        'HWREacSExe': 0.0001,
        'SWM': 0.0001
    }
}

process_name = 'SmaAsn1'
sm_hw_variant = 'FSMF'

print USAGE_CRITICAL_USAGE_VALUE[sm_hw_variant].get(process_name, 250000)

