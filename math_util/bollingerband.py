import numpy as np
import logging

logger = logging.getLogger(__name__)

def get_standard_deviation(date_value_list,sample_size=20):
    '''with date_value_list [[date,value], ...] as input source
    to calculate the standard deviation for the value part
    with element count specified by sample_size
    and return date_sd_list [[date,sd], ...]'''
    value_list = [t_entry[1] for t_entry in date_value_list]
    logger.debug('get_standard_deviation for list %s with sample size %s' % (str(value_list),
                                                                         sample_size))
    sd_list = []
    x = sample_size
    while x <= len(value_list):
        array2consider = value_list[x-sample_size:x]
        logger.debug('get_standard_deviation array2consider %s' % str(array2consider))
        standev = np.std(array2consider)
        logger.debug('get_standard_deviation element result %s' % standev)
        sd_list.append([date_value_list[x-1][0],standev])
        x += 1
    
    logger.debug('get_standard_deviation result %s' % str(sd_list))    
    return sd_list
        

def get_moving_average(date_value_list, sample_size=20):
    '''with date_value_list [[date,value], ...] as input source
    to calculate the moving average for the value part
    with element count specified by sample_size
    and return date_ave_list [[date,average], ...]'''
    date_list = [t_entry[0] for t_entry in date_value_list]
    logger.debug('get_moving_average for list %s with sample size %s' % (str(date_value_list),
                                                                  sample_size))
    value_list = [t_entry[1] for t_entry in date_value_list]
    weights = np.repeat(1.0, sample_size)/sample_size
    smas_list = np.convolve(value_list, weights, 'valid')
    date_ave_list = [list(a) for a in zip(date_list[sample_size-1:],smas_list)]

    logger.debug('get_moving_average result %s' % str(date_ave_list))    
    return date_ave_list
    
def get_bollinger_band(date_value_list, sample_size=20, std_weight=1.0):
    '''with date_value_list [[date,value], ...] as input source
    to calculate the Bollinger Band for the value part
    with element count specified by sample_size
    and standard deviation weight specified by std_weight
    and return date_bb_list [[date,bb2,bb1,sma,tb1,tb2], ...]'''
    
    bb_list = []
    sma = get_moving_average(date_value_list, int(sample_size))
    sd_list = get_standard_deviation(date_value_list, int(sample_size))
    #logging.debug('sma:\n' + str(sma) + '\nsd:\n' + str(sd_list))

    x = 0
    while x < len(sma):
        curDate = sma[x][0]
        curSMA = sma[x][1]
        curSD = sd_list[x][1]
        TB1 = curSMA + curSD*float(std_weight)
        TB2 = curSMA + curSD*2*float(std_weight)
        BB1 = curSMA - curSD*float(std_weight)
        BB2 = curSMA - curSD*2*float(std_weight)
        
        bb_list.append([curDate,BB2,BB1,curSMA,TB1,TB2])
        x += 1

    logger.debug('get_bollinger_band result %s' % str(bb_list))    
    return bb_list
        