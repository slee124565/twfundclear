from django.test import TestCase

from math_util import bollingerband

class MathUtilTestCase(TestCase):
    def setUp(self):
        self.t_list = [[n,n] for n in range(1,61)]
    
    def test_standard_deviation(self):
        
        result_list = bollingerband.get_standard_deviation(self.t_list)
        self.assertEqual(len(result_list), 41, 
                        'There should 41 element return for total 60 element with 20 element frame')
        for entry in result_list:
            self.assertEqual("{:.5f}".format(entry[1]), '5.76628', 
                        'value %s in result list should be 5.76628' % "{:.5f}".format(entry[1]))
            
    
    def test_moving_average(self):
        
        base_value = 10.5
        result_list = bollingerband.get_moving_average(self.t_list)
        for entry in result_list:
            self.assertEqual(entry[1], base_value, 
                             'element value check fail (%s, %s)' % (entry[1],base_value) )
            base_value += 1
        
    def test_bollinger_band(self):
        
        bb_list = bollingerband.get_bollinger_band(self.t_list)
        self.assertEqual(len(bb_list), 41, 
                         'total list count %s should be 41' % len(bb_list))