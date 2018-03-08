import copy
import collections
import string
from math import log


class NaiveBayesClassifier:
    
    def __init__(self, alpha):
        self.alpha = alpha
        self.defdict = collections.defaultdict()
        self.probability = collections.Counter()
        pass


    def fit(self, X, y):
        """ Fit Naive Bayes classifier according to X, y. """
        classes = set(y)
        for i in range(len(X)):
            words = X[i].split(' ')
            for word in words:
                if word not in self.defdict:
                    self.defdict[word] = {i: [0, 0] for i in classes}
                self.defdict[word][y[i]][0] += 1

        d = len(self.defdict)
        counter = collections.Counter()
        for word in self.defdict:
            for elem in classes:
                counter[elem] += self.defdict[word][elem][0]

        for word in self.defdict:
            for elem in classes:
                self.defdict[word][elem][1] = ((self.defdict[word][elem][0] + self.alpha) / 
                                               (counter[elem] + self.alpha * d))

        self.probability = collections.Counter(y)
        for elem in self.probability:
            self.probability[elem] /= len(y)
            self.probability[elem] = round(log(self.probability[elem])) 
            
    def predict(self, X):
        """ Perform classification on an array of test vectors X. """
        y = []
        for i in X:
            copy_classes = self.probability.copy()
            words = i.split(" ")
            for word in words:
                for elem in self.probability:
                    copy_classes[elem] += calculate(word, elem, self.defdict)

            y.append(prediction(copy_classes))                            
        return y                
    
    def score(self, X_test, y_test):
        """ Returns the mean accuracy on the given test data and labels. """
        count = 0
        predict = self.predict(X_test)
        for i in range(len(predict)):
            if y_test[i] == predict[i]:
                count += 1
        return count / len(y_test)


def prediction(copy_classes):
    maximum = -10000000
    for i in copy_classes:
        if copy_classes[i] > maximum:
            key = i
            maximum = copy_classes[i]
    return key        


def calculate(word, elem, defdict):
    try:
        value = defdict[word][elem][1]
    except KeyError:
        value = 0   
    if value == 0:
        return 0
    else:
        return log(value)


def clean(s):
    translator = str.maketrans("", "", string.punctuation)
    return s.translate(translator)
       
