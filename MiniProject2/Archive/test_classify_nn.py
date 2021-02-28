import sys
import numpy as np
from sklearn.model_selection import train_test_split

from Gesture import GestureSet, Sequence, Frame
from classify_nn import classify_nn
from normalize_frames import normalize_frames
from load_gestures import load_gestures

""" NOT RANDOM
def split(num_frames, ratio, norm_gesture_sets):
    num_sequences = len(norm_gesture_sets[0].sequences)
    split = int(ratio*num_sequences)
    test_sequences = []
    for gesture_set in norm_gesture_sets:
        seq = gesture_set.sequences
        train = seq[0:split]
        test = seq[split:]
        gesture_set.sequences = train
        for t in test:
            test_sequences.append(t)
    return norm_gesture_sets, test_sequences
"""

#RANDOM
def split(num_frames, ratio, norm_gesture_sets):
    num_sequences = len(norm_gesture_sets[0].sequences)
    split = int(ratio*num_sequences)
    test_sequences = []
    for gesture_set in norm_gesture_sets:
        seq = gesture_set.sequences
        train = set()
        while len(train) < split:
            i = np.random.randint(0, len(seq)-1)
            train.add(i)
        test = set([i for i in range(len(seq))]) - train
        test = sorted(test)[::-1]
        for i in test:
            test_seq = gesture_set.sequences.pop(i)
            test_sequences.append(test_seq)
    return norm_gesture_sets, test_sequences


def test_classify_nn(num_frames, ratio):
    """
    Tests classify_nn function. 
    Splits gesture data into training and testing sets and computes the accuracy of classify_nn()
    :param num_frames: the number of frames to normalize to
    :param ratio: percentage to be used for training
    :return: the accuracy of classify_nn()
    """

    gesture_sets = load_gestures()
    norm_gesture_sets = normalize_frames(gesture_sets, num_frames)
    splt = int(ratio*len(gesture_sets))
    test_gesture_sets, test_sequences = split(num_frames, ratio, norm_gesture_sets)
    correct = 0
    for test in test_sequences:
        result = classify_nn(test, norm_gesture_sets)
        actual = test.label
        if int(result) == int(actual):
            correct +=1
    return correct/len(test_sequences)


if len(sys.argv) != 3:
    raise ValueError('Error! Give normalized frame number and test/training ratio after filename in command. \n'
                     'e.g. python test_nn.py 20 0.4')

num_frames = int(sys.argv[1])
ratio = float(sys.argv[2])

accuracy = test_classify_nn(num_frames, ratio)
print("Accuracy: ", accuracy)