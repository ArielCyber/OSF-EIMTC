from EIMTC.metrics import accuracy_score


def multi_label_accuracy_score(y_true, y_pred, **kwargs):
    scores = []
    for true, pred in zip(y_true, y_pred):
        scores.append(accuracy_score(true, pred))
    
    return tuple(scores)


def multi_label_tuple_accuracy_score(y_true, y_pred):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    score = (y_true.T == y_pred.T)[:,0]
    for i in range(1, y_true.shape[0]):
        score = score & (y_true.T == y_pred.T)[:,i]

    match_count = len(score[score == True])
    sample_count = y_true.shape[1]
    accuracy = match_count/sample_count
    
    return accuracy