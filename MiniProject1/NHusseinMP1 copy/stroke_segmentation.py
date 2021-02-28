import math
import numpy as np
import scipy.io
import matplotlib.pyplot as plt
from matplotlib import patches

from detect_peaks import detect_peaks
from circle_fit import circle_fit

# If matplotlib is not working on OSX follow directions in the link below
# https://stackoverflow.com/questions/21784641/installation-issue-with-matplotlib-python


# parameters
PEN_SMOOTHING_WINDOW = 5 
TANGENT_WINDOW = 11
CURVATURE_WINDOW = 11
SPEED_THRESHOLD_1 = .5 #a percentage of the average speed
CURVATURE_THRESHOLD = .85 #in degrees per pixel
SPEED_THRESHOLD_2 = .95 #a percentage of the average speed
MINIMUM_DISTANCE_BETWEEN_CORNERS = 160
MINIMUM_ARC_ANGLE = 30 #in degrees
MERGE_LENGTH_THRESHOLD = .2
MERGE_FIT_ERROR_THRESHOLD = .1

def distance(p1, p2):
    """
    Computes distance between two Stroke points
    """
    return ((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)**(0.5)


def compute_cumulative_arc_lengths(stroke):
    """
    param stroke : a Stroke object with N x,y,t data points

    return : the array (length N) of the cumulative arc lengths between each pair
        of consecutive sampled points in a stroke of length N.
    """

    #TODO: your part 1 code here
    arc_lengths = [0]
    for i in range(1, len(stroke.x)):
        p1 = (stroke.x[i-1], stroke.y[i-1])
        p2 = (stroke.x[i], stroke.y[i])
        d = distance(p1, p2)
        arc_lengths.append(d+arc_lengths[-1])
    return arc_lengths

def find_speed(d1, d2, t1, t2):
    return abs((d2-d1)/(t2-t1))

def plot_speeds(stroke, speeds):
    t = [i for i in range(len(stroke.x))]
    plt.plot(t, speeds)
    plt.show()

def compute_speeds(stroke, cumulative_arc_lengths):
    speeds = [0]
    for i in range(1, len(stroke.x)-1):
        d1 = cumulative_arc_lengths[i-1]
        t1 = stroke.t[i-1]
        d2 = cumulative_arc_lengths[i+1]
        t2 = stroke.t[i+1]
        speed = find_speed(d1, d2, t1, t2)
        speeds.append(speed)
    if len(speeds) >=2:
        speeds[0] = speeds[1]
    speeds.append(speeds[-1])
    return speeds

def compute_smoothed_pen_speeds(stroke, cumulative_arc_lengths,
    window=PEN_SMOOTHING_WINDOW):
    """
    param stroke : a Stroke object with N x,y,t data points
    param cumulative_arc_lengths : array of the cumulative arc lengths of the
        stroke
    param window : size of the window over which smoothing occurs

    return : an array (length N) of the smoothed pen speeds at each point on
        a stroke of length N.
    """
    #TODO: your part 2 code here
    speeds = compute_speeds(stroke, cumulative_arc_lengths)

    smoothed_speeds = []
    for i in range(len(speeds)):
        to_avg = []
        for j in range(-int(window/2), int(window/2)+1):
            if j+i >=0 and j+i < len(speeds):
                to_avg.append(speeds[j+i])
        speed_sum = sum(to_avg)
        avg = speed_sum/len(to_avg)
        smoothed_speeds.append(avg)
    return smoothed_speeds
    

def compute_tangents(stroke, window=TANGENT_WINDOW):
    """
    param stroke : a Stroke object with N x,y,t data points
    param window : size of the window over which you calculate the regression

    return : an array (length N) of tangents
    """

    #TODO: your part 3 code here
    tangents = []
    for i in range(len(stroke.x)):
        x = []
        y = []
        for j in range(-int(window/2), int(window/2)+1):
            if j+i >=0 and j+i < len(stroke.x):
                x.append(stroke.x[j+i])
                y.append(stroke.y[i+j])
        A = np.vstack([x, np.ones(len(x))]).T
        m, b = np.linalg.lstsq(A, y, rcond = None)[0]
        tangents.append(m)
    return tangents

def compute_angles(stroke, tangents):
    """
    param stroke : a Stroke object with N x,y,t data points
    param tangents : an array of tangents (length N)

    return : an array of angles (length N)
    """

    #TODO: your part 4a code here
    return [math.atan(slope) for slope in tangents]


def plot_angles(stroke, angles):
    """
    param stroke : a Stroke object with N x,y,t data points
    param angles : an array of angles

    return : nothing (but should show a plot)
    """

    #TODO: your part 4b code here
    t = [i for i in range(len(stroke.x))]
    plt.plot(t, angles)
    plt.show()
    return

def correct_angles(stroke, angles):
    """
    param stroke : a Stroke object with N x,y,t data points
    param angles : an array of angles (length N)

    return : an array of angles (length N) correcting for the phenomenon you find
    """

    #TODO: your part 4c code here
    #return [abs(angle) for angle in angles]
    new_angles = [angles[0]]
    toAdd = 0
    for i in range(1, len(stroke.x)):
        if angles[i-1]-angles[i]>=0.5*math.pi:
            toAdd += math.pi
        if angles[i-1]-angles[i]<=-0.5*math.pi:
            toAdd -= math.pi
        new_angles.append(angles[i]+toAdd)
    return new_angles

def compute_curvatures(stroke, cumulative_arc_lengths, angles,
    curvature_window=CURVATURE_WINDOW):
    """
    param stroke : a Stroke object with N x,y,t data points
    param cumulative_arc_lengths : an array of the cumulative arc lengths of a stroke
    param angles : an array of angles
    param curvature_window : size of the window over which you calculate the least squares line

    return : an array of curvatures
    """

    #TODO: your part 4d code here
    curvatures = [0]
    for i in range(1, len(stroke.x)):
        arc_lengths = []
        tans = []
        for j in range(-int(curvature_window/2), int(curvature_window/2)+1):
            if j+i >=0 and j+i < len(stroke.x):
                arc_lengths.append(cumulative_arc_lengths[j+i])
                tans.append(angles[j+i])
        A = np.vstack([arc_lengths, np.ones(len(arc_lengths))]).T
        m, b = np.linalg.lstsq(A, tans, rcond = None)[0]
        curvatures.append(m)
    return curvatures

def compute_corners_using_speed_alone(stroke, smoothed_pen_speeds,
    speed_threshold_1=SPEED_THRESHOLD_1):
    """
    param stroke : a Stroke object with N x,y,t data points
    param smoothed_pen_speeds : an array of the smoothed pen speeds at each point on a stroke.
    param speed_threshold_1 : a percentage (between 0 and 1). The threshold determines the
        maximum percentage of the average pen speed allowed for a point to be considered a
        segmentation point.

    return : a list of all segmentation points
    """

    #TODO: your part 5a code here
    avg_speed = sum(smoothed_pen_speeds)/len(smoothed_pen_speeds)
    threshold = speed_threshold_1*avg_speed
    peaks = detect_peaks(smoothed_pen_speeds, mph = -threshold, valley = True)
    return [i for i in peaks]


def compute_corners_using_curvature_and_speed(stroke, smoothed_pen_speeds, curvatures,
    curvature_threshold=CURVATURE_THRESHOLD, speed_threshold_2=SPEED_THRESHOLD_2):
    """
    param stroke : a Stroke object with N x,y,t data points
    param smoothed_pen_speeds : an array of the smoothed pen speeds at each point on a stroke.
    param curvatures : an array of curvatures
    param curvature_threshold : in degress per pixel. The minimum threshold for the curvature of
        a point for the point to be considered a segmentation point.
    param speed_threshold_2 : a percentage (between 0 and 1). The threshold determines the
        maximum percentage of the average pen speed allowed for a point to be considered a
        segmentation point.


    return : a list of all segmentation points
    """
    #TODO: your part 5b code here
    avg_speed = sum(smoothed_pen_speeds)/len(smoothed_pen_speeds)
    s_threshold = speed_threshold_2*avg_speed
    c_threshold = math.radians(curvature_threshold)
    curvatures = [abs(i) for i in curvatures]
    peaks = detect_peaks(curvatures, mph = c_threshold)
    new_peaks = [i for i in peaks if smoothed_pen_speeds[i] <= s_threshold]
    return new_peaks



def combine_corners(stroke, cumulative_arc_lengths, corners_using_speed_alone,
    corners_using_curvature_and_speed, minimum_distance_between_corners=MINIMUM_DISTANCE_BETWEEN_CORNERS):
    """
    param stroke : a Stroke object with N x,y,t data points
    param cumulative_arc_lengths : an array of the cumulative arc lengths of the stroke
    param corners_using_speed_alone : a list of all segmentation points found using speed
    param corners_using_curvature_and_speed : a list of all segmentation points found using
        curvature and speed
    param minimum_distance_between_corners : minimum distance allowed between two segmentation
        points.

    return : a list of all segmentation points, with nearly coincident points removed. The list
    should be sorted from first to last segmentation point along the stroke.
    """
    #TODO: your part 6 code here
    corners = [0, len(stroke.x)-1]
    potentialCorners = corners_using_speed_alone + corners_using_curvature_and_speed
    for i in potentialCorners:
        toAdd = True
        for j in corners:
            if abs(cumulative_arc_lengths[j]-cumulative_arc_lengths[i]) <= minimum_distance_between_corners:
                toAdd = False
        if toAdd:
            corners.append(i)
    corners = sorted(corners, key = lambda x: stroke.t[x])
    return corners

def lin_error(m, b, x, y):
    y_lin = m*x+b
    diff = abs(y-y_lin)
    return (diff)**2

def compute_linear_error(stroke, start_point, end_point):
    """
    param stroke : a Stroke object with N x,y,t data points
    param start_point : a segmentation point, representing the index into the stroke
        where the segment begins
    param end_point : a segmentation point, respresenting the index into the stroke
        where the segment ends

    return : the residual error of the linear fit
    """

    #TODO: your part 7a code here
    X = stroke.x[start_point:end_point+1]
    Y = stroke.y[start_point:end_point+1]
    A = np.vstack([X,np.ones(len(X))]).T
    m, b = np.linalg.lstsq(A,Y, rcond = None)[0]
    sum_ = 0
    for i in range(len(X)):
        sum_ += lin_error(m, b, X[i], Y[i])
    avg = sum_/len(X)
    return avg

def circle_error(r, x_cen, y_cen, x, y):
    c = (x_cen, y_cen)
    p1 = (x, y)
    dist = distance(c, p1)-r
    return (dist)**2


def compute_circular_error(stroke, start_point, end_point):
    """
    param stroke : a Stroke object with N x,y,t data points
    param start_point : a segmentation point, representing the index into the stroke
        where the segment begins
    param end_point : a segmentation point, respresenting the index into the stroke
        where the segment ends

    return : the residual error of the circle/curve fit
    """

    #TODO: your part 7a code here
    X = stroke.x[start_point:end_point+1]
    Y = stroke.y[start_point:end_point+1]
    x_cen, y_cen, r = circle_fit(X, Y)
    sum_ = 0
    for i in range(len(X)):
        sum_ += circle_error(r, x_cen, y_cen, X[i], Y[i])
    avg = sum_/len(X)
    return avg

def compute_subtended_angle(stroke, start_point, end_point):
    """
    param stroke : a Stroke object with N x,y,t data points
    param start_point : a segmentation point, representing the index into the stroke
        where the segment begins
    param end_point : a segmentation point, respresenting the index into the stroke
        where the segment ends

    return : the angle subtended by the arc of the circle fit to the segment
    """
    #TODO: your part 7b code here
    X = stroke.x[start_point:end_point+1]
    Y = stroke.y[start_point:end_point+1]
    x_cen, y_cen, r = circle_fit(X, Y)
    c = (x_cen, y_cen)

    x1 = X[0]
    x2 = X[-1]
    y1 = Y[0]
    y2 = Y[-1]
    p1 = (x1, y1)
    p2 = (x2, y2)
    num = 2*r**2-distance(p1, p2)**2
    den = 2*r**2

    
    if num/den > 1: #edge cases
        return math.acos(1)*180/math.pi
    if num/den < -1:
        return math.acos(-1)*180/math.pi
    

    angle = math.acos(num/den)*180/(math.pi)

    return angle

def choose_segment_type(stroke, linear_error, circular_error, subtended_angle, minimum_arc_angle=MINIMUM_ARC_ANGLE):
    """
    param stroke : a Stroke object with N x,y,t data points
    param linear_error : residual error of the linear fit of the segment
    param circular_error : residual error of the circular fit of the segment
    param subtended_angle : angle subtended by the arc of the circle
    param minimum_arc_angle : minimum angle necessary for classification as a curve

    return : 0 if the segment should be a line; 1 if the segment should be a curve
    """

    #TODO: your part 7c code here
    if linear_error <= circular_error:
        return 0
    else:
        if subtended_angle > minimum_arc_angle:
            return 1
    return 0

def merge(stroke, segpoints, segtypes):
    """
    TODO (optional): define your function signature. You may change the function signature,
    but please name your function 'merge'. You may use helper functions.
    """

    #TODO (optional): your part 10 code here

    return segpoints, segtypes

def segment_stroke(stroke):
    """
    param stroke : a Stroke object with N x,y,t data points

    return :
        segpoints : an array of length M containing the segmentation points
            of the stroke. Each element in the array is an index into the stroke.
        segtypes : an array of length M-1 containing 0's (indicating a line)
            and 1's (indicating an arc) that describe the type of segment between
            segmentation points. Element i defines the type of segment between
            segmentation points i and i+1.
    """

    segpoints, segtypes = [], []

    # PART 1
    cumulative_arc_lengths = compute_cumulative_arc_lengths(stroke)

    # PART 2
    smoothed_pen_speeds = compute_smoothed_pen_speeds(stroke, cumulative_arc_lengths)

    # PART 3
    tangents = compute_tangents(stroke)

    # PART 4
    angles = compute_angles(stroke, tangents)
    #plot_angles(stroke, angles)
    corrected_angles = correct_angles(stroke, angles)
    #plot_angles(stroke, corrected_angles)
    curvatures = compute_curvatures(stroke, cumulative_arc_lengths, corrected_angles)

    # PART 5
    corners_using_speed_alone = compute_corners_using_speed_alone(stroke, smoothed_pen_speeds)
    corners_using_curvature_and_speed = compute_corners_using_curvature_and_speed(stroke, smoothed_pen_speeds, curvatures)

    # PART 6
    segpoints = combine_corners(stroke, cumulative_arc_lengths, corners_using_speed_alone, corners_using_curvature_and_speed)

    # PART 7
    for i in range(len(segpoints) - 1):
        start_point = segpoints[i]
        end_point = segpoints[i+1]
        linear_error = compute_linear_error(stroke, start_point, end_point)
        circular_error = compute_circular_error(stroke, start_point, end_point)
        subtended_angle = compute_subtended_angle(stroke, start_point, end_point)
        segment_type = choose_segment_type(stroke, linear_error, circular_error, subtended_angle)
        segtypes.append(segment_type)

    # OPTIONAL: PART 10
    segpoints, segtypes = merge(stroke, segpoints, segtypes)

    return segpoints, segtypes
