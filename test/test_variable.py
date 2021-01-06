from nose import tools
from auto_qc import variable

def test_is_variable_path_valid_with_valid_path():
    path = ':ref/metric_1'
    analysis = {
      'metadata' : {},
      'data' : {
        'ref' : {
        'metric_1' : 2 }}}
    tools.assert_true(variable.is_variable_path_valid(analysis, path))

def test_is_variable_path_valid_with_invalid_path():
    path = ':unknown/metric_1'
    analysis = {
      'metadata' : {},
      'data' : {
        'ref' : {
        'metric_1' : 2 }}}
    tools.assert_false(variable.is_variable_path_valid(analysis, path))

def test_get_variables_with_no_nesting():
    qc_node = ['<', ':ref/metric_1', 1]
    tools.assert_equal(variable.get_variable_names(qc_node), [':ref/metric_1'])

def test_get_variables_with_nesting():
    qc_node = [['and', ['or', [':ref/metric_1', 2, 1], [':ref/metric_2', 2, 1]]]]
    expected = [':ref/metric_1', ':ref/metric_2']
    tools.assert_equal(variable.get_variable_names(qc_node), expected)
