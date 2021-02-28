import math
from stroke_segmentation import segment_stroke

def distance(p1, p2):
    """
    Computes distance between two Stroke points
    """
    return ((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)**(0.5)

def normalize_segpoints(stroke):
    """
    param stroke : a Stroke object with N x,y,t data points

    return :
        (template_x, template_y): a tuple of arrays representing the normalized X
        and Y coordinates, ordered by time, of the points to be
        used in the MHD calculation to compare against the given templates

        Coordinates are normalized so that points span between 0 and 1

        Relevant points would be the full set of stroke segment endpoints
        and the curve segment midpoints

    """
    #NORMALIZE THE STROKE POINTS
    segpoints, segtypes = segment_stroke(stroke)
    #print("PTS", segpoints)
    #print("TYPES", segtypes)
    x = []
    y = []
    
    for j in range(len(segpoints)-1):
        i = segpoints[j]
        x.append(stroke.x[i])
        y.append(stroke.y[i])
        if segtypes[j] == 1:
            start = i
            end = segpoints[j+1]
            mid = int((start+end)/2)
            x.append(stroke.x[mid])
            y.append(stroke.y[mid])
    last = segpoints[-1]
    x.append(stroke.x[last])
    y.append(stroke.y[last])
    max_x = max(x)
    max_y = max(y)
    min_x = min(x)
    min_y = min(y)
    x_norm = [(i-min_x)/(max_x-min_x) for i in x]
    y_norm = [(i-min_y)/(max_y-min_y) for i in y]

    #GET THE SET OF POINTS TO BE USED IN THE MHD CALCULATION

    return (x_norm,y_norm)

def find_average(A_x, A_y, B_x, B_y):
    sum_ = 0
    for i in range(len(A_x)):
        minB = float('inf')
        for j in range(len(B_x)):
            p1 = (A_x[i], A_y[i])
            p2 = (B_x[j], B_y[j])
            d = distance(p1, p2)
            if d < minB:
                minB = d
        sum_ += minB
    return sum_/len(A_x)

def calculate_MHD(stroke, template):
    """
    param stroke : a Stroke object with N x,y,t data points
    param template : a Template object with x,y template points and name

    return :
        float representing the Modified Hausdorf Distance of the normalized segpoints
        and the template points,
        The formula for the Modified Hausdorf Distance can be found in the
        paper "An image-based, trainable symbol recognizer for
        hand-drawn sketches" by Kara and Stahovichb

    """
    stroke_x, stroke_y = normalize_segpoints(stroke)
    template_x, template_y = [template.x, template.y]
    hmodAB = find_average(stroke_x, stroke_y, template_x, template_y)
    hmodBA = find_average(template_x, template_y, stroke_x, stroke_y)
    return max(hmodAB, hmodBA)

def classify_stroke(stroke, templates):
    """
    param stroke : a Stroke object with N x,y,t data points
    param templates: a list of Template objects, each with name, x, y
                     Each template represents a different symbol.

    return :
        string representing the name of the best matched Template of a stroke
    """
    #return None
    final_template = None
    min_MHD = float('inf')
    for t in templates:
        mhd = calculate_MHD(stroke, t)
        if mhd < min_MHD:
            min_MHD = mhd
            final_template = t
    return final_template.name
