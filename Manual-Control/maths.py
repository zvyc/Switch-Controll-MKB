def clamp_mouse_coords(num, min_value, max_value):
    value = max(min(num, max_value), min_value)
    if value == 128:
    	return value
    elif value > 128:
    	return max(min(num+25, max_value), min_value)
    elif value < 128:
    	return max(min(num-25, max_value), min_value)

def clamp(num, min_value, max_value):
	return max(min(num, max_value), min_value)
