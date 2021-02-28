from Gesture import GestureSet, Sequence, Frame

def normalize_frames(gesture_sets, num_frames):
    """
    Normalizes the number of Frames in each Sequence in each GestureSet
    :param gesture_sets: the list of GesturesSets
    :param num_frames: the number of frames to normalize to
    :return: a list of GestureSets where all Sequences have the same number of Frames
    """
    new_gesture_sets = [i for i in gesture_sets]
    for gesture_set in new_gesture_sets:
    	for sequence in gesture_set.sequences:
    		normalize_sequence(sequence, num_frames)
    return new_gesture_sets


def normalize_sequence(sequence, num_frames):
	current_length = len(sequence.frames)
	new_frames = []
	if current_length == num_frames:
		return
	if current_length < num_frames:
		indices = add_frames(sequence, num_frames)
		new_frames = [sequence.frames[i] for i in indices]
	if current_length > num_frames:
		indices = remove_frames(sequence, num_frames)
		new_frames = [sequence.frames[i] for i in indices]
	sequence.frames = new_frames[0:]

def remove_frames(sequence, num_frames):
	current_length = len(sequence.frames)
	step = current_length/float(num_frames-1)
	toKeep = {0}
	remove = [round(i*step) for i in range(1, num_frames-1)]
	toKeep = [0] + remove + [current_length-1]
	return sorted(list(toKeep))

def add_frames(sequence, num_frames):
	current_length = len(sequence.frames)
	toAdd = num_frames - current_length 
	step = current_length/toAdd
	offset = (current_length%toAdd)/2
	add = [int(i*step) for i in range(toAdd)]
	return sorted([i for i in range(current_length)] + add)



