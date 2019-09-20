import argparse
import sys


defaults = {	
	'num_of_sides' 		: 4,
	'visualize'     	: False,
	'save'          	: False,
	'img_height'    	: 200,
	'img_width'     	: 200,
	'padding'       	: 10,
	'min_angle'     	: 30,
	'min_side_length' 	: 30,
	'max_iter'			: 20
}

parser = argparse.ArgumentParser()

parser.add_argument('--num_of_sides', default=defaults['num_of_sides'], type=int, help="Define the number of sides for the polygon.")
parser.add_argument('--visualize', action='store_true', default=defaults['visualize'], help="If you want to visualize the working of the algorithm")
parser.add_argument('--save', action='store_true', default=defaults['save'], help='If you want to save the end result as an image.')
parser.add_argument('--min_angle', default=defaults['min_angle'], type=int, help='Define the minimum angle between each adjacent sides.')
parser.add_argument('--min_side_length', default=defaults['min_side_length'], type=int, help='Define the minimum length for each side.')
parser.add_argument('--max_iter', default=defaults['max_iter'], type=int, 
					help='Define the maximum number of iteration that the algorithm should try to meet the criterias. If it is not met within the specified value, the algorithm will restart again.')
parser.add_argument('--height', default=defaults['img_height'], type=int, help='Define the image height')
parser.add_argument('--width', default=defaults['img_width'], type=int, help='Define the image width.')
parser.add_argument('--padding', default=defaults['padding'], type=int, 
				help='Define the padding size. Padding is used to make sure the points generated are not too close to the image boundary.')


args = parser.parse_args()

assert args.num_of_sides >= 3, "Number of sides must be more than 2 !"
assert args.height >= 20, "Image height must be at least 20!"
assert args.width >= 20, "Image width must be at least 20!"
assert args.padding*2 <= args.width or args.padding*2 <= args.height, "Padding size cannot exceed half of the width nor height of the image!"
assert args.min_side_length < args.height or args.min_side_length < args.width, "The length of the sides cannot exceed the width nor the height of the image!"
assert args.min_angle > 0, "The minimum angle must be more than 0!"
assert args.max_iter > 0, "The maximum iteration value must be more than 0!"