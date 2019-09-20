import cv2
import numpy as np 
import random
import math
import cfg

args = cfg.args

image_height = args.height
image_width = args.width
padding = args.padding 

min_side_length = args.min_side_length
min_angle = args.min_angle
max_angle = 180 - min_angle

sides = args.num_of_sides

max_iter = args.max_iter

image = np.zeros((image_height, image_width, 3))



def draw_temp_line(im, point1, point2, red_colour=255):

	#copy the image so that the original image is unaffected
	img = im.copy()

	cv2.line(img, (point1[0], point1[1]),
				  (point2[0], point2[1]),
				  (255,255,red_colour),1)

	return img



def list2numpy(given_list):
	'''
	Convert the given list into a np array
	'''

	return np.asarray(given_list, dtype='int32')



def bool_orientation(vector1, vector2):
	'''
	Calculates the cross product between two vectors. Positive value denotes an anti clockwise direction.
	KEEP IN MIND that when plotted in an image, the direction will be reversed since the origin in an image
	starts from the top left.
	'''

	cross_product = np.cross(vector1, vector2)

	if cross_product > 0:

		return True

	return False


def bool_angle(vector1, vector2):
	'''
	Calculates the angle between two vectors and check if the angle meets the required criteria.
	'''

	#length of the vectors
	vector1_len = np.linalg.norm(vector1) 
	vector2_len = np.linalg.norm(vector2)

	#get the cosine value
	cos_theta = vector1.dot(vector2)/(vector1_len*vector2_len)

	#the values can sometimes reach slightly above 1 or below negative 1 
	#due to the floating point errors
	if cos_theta > 1 : cos_theta = 1
	if cos_theta < -1 : cos_theta = -1

	#calculate the angle in degree
	angle = math.degrees(math.acos(cos_theta))

	return min_angle <= angle <= max_angle


def bool_length(point1, point2):
	'''
	Check if the distance between two points meets the required criteria.
	'''
	point1 = list2numpy(point1)
	point2 = list2numpy(point2)

	vector = point1 - point2 

	length = np.linalg.norm(vector)

	if length < min_side_length:

		return False

	return True


def generate_point():
	'''
	Generate a point based on the given criteria.
	'''
	point = [random.randint(padding, image_width-padding), random.randint(padding, image_height-padding)]

	return point


def generate_polygon(visualize=False):
	'''
	To generate a polygon based on the number of sides. 
	1) Randomly generates two points.
	2) Generates the next point and check if
	   a) the new point is in the anti-clockwise direction
	   b) if it meets the min-max requirement for length and angle
	3) If the requirements in second step cannot be met after max_iter times, the whole process will be repeated.
	'''
	global img_idx
	status = False 
	
	while not status:

		all_points = {}

		#generate two random points 
		first_point  = generate_point()
		second_point = generate_point()

		#if the length is below minimum
		while not bool_length(first_point, second_point):

			#generate two random points 
			first_point  = generate_point()
			second_point = generate_point()

		all_points['p1'] = first_point
		all_points['p2'] = second_point

		#plot the first two points
		if visualize:

			img = draw_temp_line(image, all_points['p1'], all_points['p2'])
			cv2.imshow('',img)
			cv2.waitKey(50)

		#initialize this to 3 since the first two points are already generated.
		point_idx = 3

		#the first vector from point p1 to p2
		first_vector = list2numpy(all_points['p2']) - list2numpy(all_points['p1'])

		iteration = 0

		while True:

			#if maximum trial has reached, generate back the two points from the start
			if iteration > max_iter:
				break

			#add a new point
			all_points['p'+str(point_idx)] = generate_point()

			#to visualize the process of selecting a point
			if visualize:

				temp_img = draw_temp_line(img, all_points['p'+str(point_idx-1)], all_points['p'+str(point_idx)], 0)
				cv2.imshow('', temp_img)
				cv2.waitKey(50)


			#if the length criteria is not met, generate again
			if not bool_length(all_points['p'+str(point_idx)], all_points['p'+str(point_idx-1)]):
				continue


			#vector from point p1 to point point_idx-1
			prev_vector    = list2numpy(all_points['p'+str(point_idx - 1)]) - list2numpy(all_points['p1'])

			#vector from point p1 to point point_idx
			curr_vector    = list2numpy(all_points['p'+str(point_idx)]) - list2numpy(all_points['p1'])

			#if the generated point is not in the counter clockwise direction, the loop will restart with a new point
			#HOWEVER NOTICE THAT THE COORDINATE SYSTEM IN IMAGES IS DIFFERENT. The origin is at the top left. Hence,
			#clockwise vectors in conventional vector space notation is reversed !
			if not bool_orientation(prev_vector, curr_vector):

				iteration +=1 
				continue

			#apart from checking each previous side with the new generated side, we also need to always
			#perform the check between the first side and the generated side to avoid getting a concave polygon.
			#If we do not perform this check, there might be a point that falls on the clockwise direction from the first side
			#while still being in the desired counter clockwise direction from its previous side.
			if not bool_orientation(first_vector, curr_vector):

				iteration +=1 
				continue

			#vector from the point (point_idx - 1) to point (point_idx - 2) 
			#i.e. vector from the one point before to current point
			left_vector  = list2numpy(all_points['p'+str(point_idx-2)]) - list2numpy(all_points['p'+str(point_idx-1)])
			#vector from the point (point_idx - 1) to point (point_idx)
			#i.e. vector from the last 2 points before to one point before
			right_vector = list2numpy(all_points['p'+str(point_idx)]) - list2numpy(all_points['p'+str(point_idx-1)])

			#the angle between the left and right vector from point (point_idx - 1) must meet the defined criteria
			if not bool_angle(left_vector, right_vector):
				iteration += 1
				continue

			#the direction from the left vector to the right vector must be clockwise
			if bool_orientation(left_vector, right_vector):

				iteration += 1
				continue

			if visualize:

				img = draw_temp_line(img, all_points['p'+str(point_idx-1)], all_points['p'+str(point_idx)])
				cv2.imshow('', img)
				cv2.waitKey(50)

			if len(all_points) == sides:

				
				#the previous side of the last point will be on the left connected to the second last point
				left_vector  = list2numpy(all_points['p'+str(point_idx - 1)]) - list2numpy(all_points['p'+str(point_idx)])

				#the last point will be connected on the right back to the first point
				right_vector = list2numpy(all_points['p1']) - list2numpy(all_points['p'+str(point_idx)])

				#check if the vector from the last point to the first point meets the defined length criteria
				if not bool_length(all_points['p'+str(point_idx)], all_points['p1']):
					break

				#the angle between both vectors must reach the defined criteria
				if not bool_angle(left_vector, right_vector):
					iteration +=1 
					continue

				#the direction from the left to right vector must be clockwise
				if bool_orientation(left_vector, right_vector) :

					iteration +=1 
					continue

				#the vector that connects from p1 to the last point
				opp_right_vector = -1 * right_vector

				#check the angle between the vector (p1 to p2) and the vector between (p1 and the last point)
				if not bool_angle(opp_right_vector, first_vector):

					iteration += 1
					continue

				#if everything succeeds, the set status to true to exit the entire loop
				status = True
				break

			point_idx += 1

	return all_points



def get_final_points(dictionary):
	'''
	Iterate through the dictionary to extract the points from point 1 to point (sides)
	'''

	points_list = []

	for i in range(1, len(dictionary)+1):

		points_list.append(dictionary['p'+str(i)])


	return points_list



def draw_lines(im, points):

	img = im.copy()

	for i in range(len(points)):

		next_index = (i+1)%len(points)

		cv2.line(img, (points[i][0], points[i][1]),
			          (points[next_index][0], points[next_index][1]),
			          (255,255,255),1)


	return img 


if __name__ == "__main__":

	dictionary = generate_polygon(args.visualize)
	final_points = get_final_points(dictionary)
	final_img = draw_lines(image, final_points)

	if args.visualize:
		cv2.imshow('', final_img)
		cv2.waitKey(0)

	if args.save:

		cv2.imwrite('result.jpg', final_img)




















