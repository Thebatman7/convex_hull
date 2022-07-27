from heapq import merge
from operator import truediv
import random
from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT6':
	from PyQt6.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

#A polygon that has all interior angles less than 180°. All the vertices point 'outwards', away from the center. That is, Convex means that the polygon has no corner that is bent inwards.
#The convex hull of a set of points is defined as the smallest convex polygon, that encloses all of the points in the set. 
import time

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
MAGENTA = (255,0,255)
AQUA = (0,255, 255)
BLACK = (0, 0, 0)
PINK = (255, 20, 147)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

# Class constructor
	def __init__( self):
		super().__init__()
		self.pause = False

# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

	def showTangent(self, line, color):
		self.view.addLines(line,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self,line,color):
		self.showTangent(line,color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseHull(self,polygon):
		self.view.clearLines(polygon)

	def showText(self,text):
		self.view.displayStatusText(text)


# Quicksort
	def sortPoints(self, points):
		if (points == []) :
			return []
		else: 
			pivot= points[0].x()
			varia= points[0]
			lesser = self.sortPoints([x for x in points[1:] if x.x() < pivot])
			greater = self.sortPoints([x for x in points[1:] if x.x() >= pivot])
			return lesser + [varia] + greater

# Prints x and y variables of the points in a list
	def printXY(self, points):
		for i in range(len(points)):
			print('%s: x: %f, y: %f' %(i, points[i].x(), points[i].y()))
# Prints x points in list of points
	def printPoints(self, points):
		for x in range(len(points)):
			if not x == len(points)-1:
				print('%s: %f, ' %(x, (points[x].x())))
			else:
				print('%s: %f' %(x, points[x].x()))
# Prints left and right side which are list of points
	#def printLR(self, left_p, right_p):
		#print("Left size: %s, values are:" %len(left_p))
		#self.printPoints(left_p)
		#print("Right size: %s, values are:" %len(right_p))
		#self.printPoints(right_p)

# Randomly creates a color 
	def ran_col(self):
		r = random.randint(0, 255)
		g = random.randint(0, 255)
		b = random.randint(0, 255)
		COLOR = (r, g, b)
		return COLOR

# Reorders the points in a clockwise order
		# Method to reorder the list in a clockwise order. This is needed so we can't have the list ordered based on the x value
		# This would not let us go through the polygon in the right order. [1, 2, 3] if 2 is lower than 1 than it shoud be 1 -> 3 -> 2 -> 1

		# Parameters:
		# points (list): A list of QpointF objects ordered based on their x value

		# Returns:
		# list: Return a list of QpointF objects ordered in clockwise order
	def ord_clockwise(self, points):
		line1 = QLineF(points[0], points[1])
		line2 = QLineF(points[0], points[2])
		# slope of a like  = rise / run
		slope1 = (line1.dy() / line1.dx())
		slope2 = (line2.dy() / line2.dx())
		if(slope1 <= slope2): # alternative swap points[1], points[2] = points[2], points[1]
			temp = points[1]
			points[1] = points[2]
			points[2] = temp
		return points

# Method to find the right most point of the left polygon O(n) this n is smaller tho.
	def find_right_most(self, left_pol):
		right_most = left_pol[0]
		x = 0
		for i in range(len(left_pol)):
			if left_pol[i].x() > right_most.x():
				right_most = left_pol[i]
				x = i
		return (x, right_most) 


# Method claculates the slope of the line that two points form
	def find_slope(self, l_point, r_point):
		line = QLineF(l_point, r_point)
		slope = (line.dy() / line.dx())
		return slope


# Divide-and-conquer. The median of a set of numbers is the middle number in the set
# Method divide-and-conquer to split points into groups of three or less, connect them and form convex hulls.

		# Parameters:
		# points (list): A list of QpointF objects

		# Returns:
		# list: Return a list of QpointF objects
	def div_con(self, points):
		if len(points) <= 3:
			if(len(points) == 3):
				points = self.ord_clockwise(points)
			# polygon = [QLineF(points[i],points[(i+1)%len(points)]) for i in range(len(points))]
			# self.showHull(polygon, BLUE)
			return points
		else:
			middle = len(points)//2 # floor
			left = points[0: middle] 
			right = points[middle:]
			#self.printLR(left, right)
			left_poly = self.div_con(left)
			right_poly = self.div_con(right)
		return self.merge(left_poly, right_poly)


# Method merge connects two lists of points (polygons) and creates a new convex hull.
# We merge them by finding the upper tangent line and lower tanget line.

		# Parameters:
		# left_pol (list): A list of points, QpointF, ordered in clockwise 
		# right_pol (list): A list of points, QpointF, ordered in clockwise 

		# Returns:
		# list: Return a list of QpointF objects ordered in clockwise order which represents the new convex hull
	def merge(self, left_pol, right_pol):

		# right polygon left most point. This will always be the first point in the right hand list
		r_anchor_point = right_pol[0] 
		r_anchor_i = 0

		# left polygon right most point. Since the list is ordered clockwise we have to iterate through the list to find the right most point of the left polygon
		answer = self.find_right_most(left_pol)
		l_anchor_i = answer[0]
		l_anchor_point = answer[1]
		

		#given two list of points ordered in clockwise order
		slope_change = True
		u_tan_slope = self.find_slope(l_anchor_point, r_anchor_point) #initial slope 
		l_tan_slope = u_tan_slope
		r_low_anchor_point = r_anchor_point
		r_low_anchor_i = r_anchor_i
		l_low_anchor_point = l_anchor_point
		l_low_anchor_i = l_anchor_i

	
		while(slope_change):
			left_change = False
			right_change = False
			# Loop for RIGHT POLYGON
			index = (r_anchor_i + 1) % len(right_pol)
			while (index < len(right_pol)):
				slope = self.find_slope(l_anchor_point, right_pol[index])
				if(slope > u_tan_slope):
					r_anchor_point = right_pol[index] # new anchor point in the right pol
					r_anchor_i = index # index of anchor point in right pol
					u_tan_slope = slope # we assign the upper tangent line
					left_change = True
					index += 1
				else:
					break

			# Loop for LEFT POLYGON
			ind = (l_anchor_i - 1) % len(left_pol) 
			while(ind >= 0):
				slope = self.find_slope(left_pol[ind], r_anchor_point)
				if(slope < u_tan_slope):
					l_anchor_point = left_pol[ind]
					l_anchor_i = ind
					u_tan_slope = slope
					right_change = True
					ind -= 1
				else:
					break
			if not left_change and not right_change: slope_change = False
		

		slope_change = True
		while(slope_change):
			left_change = False
			right_change = False
			# Loop for RIGHT POLYGON
			i = (r_low_anchor_i - 1) % len(right_pol)
			while (i >= 0):
				slope = self.find_slope(l_low_anchor_point, right_pol[i])
				if(slope < l_tan_slope):
					r_low_anchor_point = right_pol[i] # new anchor point in the right pol
					r_low_anchor_i = i # index of anchor point in right pol
					l_tan_slope = slope # we assign the upper tangent line
					left_change = True
					i -= 1
				else:
					break

			# Loop for LEFT POLYGON
			index_ = (l_low_anchor_i + 1) % len(left_pol) 
			while(index_ < len(left_pol)):
				slope = self.find_slope(left_pol[index_], r_low_anchor_point)
				if(slope > l_tan_slope):
					l_low_anchor_point = left_pol[index_]
					l_low_anchor_i = index_
					l_tan_slope = slope
					right_change = True
					index_ += 1
				else:
					break
			if not left_change and not right_change: slope_change = False
		
		# line = QLineF(l_low_anchor_point,r_low_anchor_point)
		# self.showTangent([line], PINK)

		poly = []
		if l_anchor_i == l_low_anchor_i:
			poly.append(left_pol[l_anchor_i])
		else:
			here = 0
			notfound = True
			while(notfound):
				if here == l_anchor_i:
					poly.append(left_pol[here])
					notfound = False
				else :
					poly.append(left_pol[here])
				here += 1
		
		if r_anchor_i == r_low_anchor_i:
			poly.append(right_pol[r_anchor_i])
		else:
			here = r_anchor_i
			notfound = True
			while(notfound):
				if here == r_low_anchor_i:
					poly.append(right_pol[here])
					notfound = False
				else:
					poly.append(right_pol[here])
				here = (here + 1) % len(right_pol)

		if not l_low_anchor_i == 0:
			notEnd = True
			here = l_low_anchor_i
			while(notEnd):
				if(here == (len(left_pol) - 1)):
					poly.append(left_pol[here])
					notEnd = False
				else:
					poly.append(left_pol[here])
				here += 1
	
		# polygon = [QLineF(poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly))]
		# COLOR = self.ran_col()
		# self.showHull(polygon, COLOR)
		return poly




			



# This is the method that gets called by the GUI and actually executes
# the finding of the hull
	def compute_hull(self, points, pause, view):
		print()
		print("-------------------------------------------NEW CALL-------------------------------------------")
		self.pause = pause
		self.view = view
		assert( type(points) == list and type(points[0]) == QPointF )

		t1 = time.time()
		# SORT THE POINTS BY INCREASING X-
		points = self.sortPoints(points)
		t2 = time.time()
		print('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t2-t1))


		t3 = time.time()
		# DIVIDE-AND-CONQUER CONVEX HULL SOLVER
		poly = self.div_con(points)
		t4 = time.time()

		polygon = [QLineF(poly[i],poly[(i+1)%len(poly)]) for i in range(len(poly))]
		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(polygon, BLACK)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))

#Helpful link:
#https://treyhunner.com/2016/04/how-to-loop-with-indexes-in-python/