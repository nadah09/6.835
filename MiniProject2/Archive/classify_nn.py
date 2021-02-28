import operator
import math
import numpy as np

def distance(A, B):
	sum_ = 0
	for i in range(len(A)):
		sum_ += (A[i]-B[i])**2
	return sum_


def find_L2(sequence, test_sequence):
	assert(len(sequence.frames) == len(test_sequence.frames))
	dist = 0
	for i in range(len(sequence.frames)):
		sframe = sequence.frames[i].frame
		tframe = test_sequence.frames[i].frame
		dist += distance(sequence.frames[i].frame, test_sequence.frames[i].frame)
	return dist


def classify_nn(test_sequence, training_gesture_sets):
	"""
	Classify test_sequence using nearest neighbors
	:param test_gesture: Sequence to classify
	:param training_gesture_sets: training set of labeled gestures
	:return: a classification label (an integer between 0 and 8)
	"""
	min_dist = float('inf')
	result = None
	for gs in training_gesture_sets:
		total = 0
		for seq in gs.sequences:
			l2 = find_L2(seq, test_sequence)
			total += l2
		avg = total/len(gs.sequences)
		if avg < min_dist:
			min_dist = avg
			result = gs.label
	return result


