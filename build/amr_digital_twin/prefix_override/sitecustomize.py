import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/barath_ros2/warehouse_ws/install/amr_digital_twin'
