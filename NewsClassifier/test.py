import NBClassifier
import csv


def test():
    with open("SMSSpamCollection", encoding='utf-8') as f:
        data = list(csv.reader(f, delimiter="\t"))    
    X, y = [], []
    for target, msg in data:
        X.append(msg)
        y.append(target)
    X = [NBClassifier.clean(x).lower() for x in X]
    X_train, y_train, X_test, y_test = X[:3900], y[:3900], X[3900:], y[3900:]
    model = NBClassifier.NaiveBayesClassifier(0.05)
    model.fit(X_train, y_train)
    print(model.score(X_test, y_test))   
