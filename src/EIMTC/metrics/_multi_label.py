from EIMTC.metrics import accuracy_score
import numpy as np

def multi_label_accuracy_score(y_true, y_pred, **kwargs):
    scores = []
    for true, pred in zip(y_true, y_pred):
        scores.append(accuracy_score(true, pred))
    
    return tuple(scores)


def multi_label_tuple_accuracy_score(y_true, y_pred):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    score = np.sum(np.all(y_true.T == y_pred.T, axis=1))

    match_count = len(score[score == True])
    sample_count = y_true.shape[1]
    accuracy = match_count/sample_count
    
    return accuracy


def multi_label_tuple_matrix(y_true, y_pred):
    results_per_class = []
    for combination in np.stack(np.meshgrid(*[np.unique(lbls) for lbls in y_true]), -1).reshape(-1, len(y_true)):
        result_dict = multi_label_tuple_for_class(y_true, y_pred, combination)
        result_dict['class'] = combination
        results_per_class.append(result_dict)
        
    return results_per_class

def multi_label_tuple_for_class(y_true, y_pred, classes):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    
    # tp
    samples_indices_for_class = np.where((y_true.T == classes).all(axis=1))[0]
    predictions_for_indices = y_pred.T[samples_indices_for_class]
    tp = np.sum(np.all(predictions_for_indices == classes, axis=1))
    # fn
    fn = np.sum(np.any(predictions_for_indices != classes, axis=1))
    # fp
    samples_indices_for_not_class = np.where((y_true.T != classes).any(axis=1))[0]
    predictions_for_indices = y_pred.T[samples_indices_for_not_class]
    fp = np.sum(np.all(predictions_for_indices == classes, axis=1))
    # tn
    tn = np.sum(np.any(predictions_for_indices != classes, axis=1))
    
    return {
        'tp': tp,
        'fp': fp,
        'tn': tn,
        'fn': fn,
    }
    
def multi_label_tuple_recall_score(y_true, y_pred, mode='class'):
    if mode == 'class':
        return multi_label_tuple_recall_score_per_tuple(y_true, y_pred)
    elif mode == 'macro':
        return multi_label_tuple_recall_score_macro(y_true, y_pred)

def multi_label_tuple_recall_score_per_tuple(y_true, y_pred):
    mat = multi_label_tuple_matrix(y_true, y_pred)
    recalls = []
    for cls in mat:
        if (cls['tp'] + cls['fn']) == 0:
            recall_for_class = 0.0
        else:
            recall_for_class = cls['tp'] / (cls['tp'] + cls['fn'])
        recalls.append(recall_for_class)
    
    return recalls
        
def multi_label_tuple_recall_score_macro(y_true, y_pred):
    recalls = multi_label_tuple_recall_score_per_tuple(y_true, y_pred)
    recall_score = np.sum(recalls)/len(recalls)
    
    return recall_score


## PRECISION ##
def multi_label_tuple_precision_score(y_true, y_pred, mode='class'):
    if mode == 'class':
        return multi_label_tuple_precision_score_per_tuple(y_true, y_pred)
    elif mode == 'macro':
        return multi_label_tuple_precision_score_macro(y_true, y_pred)

def multi_label_tuple_precision_score_per_tuple(y_true, y_pred, mode='class'):
    mat = multi_label_tuple_matrix(y_true, y_pred)
    precisions = []
    for cls in mat:
        if (cls['tp'] + cls['fp']) == 0:
            recall_for_class = 0.0
        else:
            recall_for_class = cls['tp'] / (cls['tp'] + cls['fp'])
        precisions.append(recall_for_class)    
        
    return precisions

def multi_label_tuple_precision_score_macro(y_true, y_pred):
    precisions = multi_label_tuple_precision_score_per_tuple(y_true, y_pred)
    precision_score = np.sum(precisions)/len(precisions)
    
    return precision_score


## F1 ##
def multi_label_tuple_f1_score(y_true, y_pred, mode='class'):
    if mode == 'class':
        return multi_label_tuple_f1_score_per_tuple(y_true, y_pred)
    elif mode == 'macro':
        return multi_label_tuple_f1_score_macro(y_true, y_pred)

def multi_label_tuple_f1_score_per_tuple(y_true, y_pred):
    mat_recall = np.asarray(multi_label_tuple_recall_score(y_true, y_pred))
    mat_precision = np.asarray(multi_label_tuple_precision_score(y_true, y_pred))
    f1_per_class = np.nan_to_num((2*mat_recall*mat_precision)/(mat_recall+mat_precision))
    
    return f1_per_class

def multi_label_tuple_f1_score_macro(y_true, y_pred):
    f1s = multi_label_tuple_f1_score_per_tuple(y_true, y_pred)
    f1_score = np.sum(f1s)/len(f1s)
    
    return f1_score