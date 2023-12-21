import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from catboost import CatBoostClassifier
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle


if __name__ == '__main__':

    print("Starting classification")

    result_string = ""

    data = pd.read_csv('data.csv')
    data = data.drop(columns=['Unnamed: 0', 'Video_number'])
    data_shuffled = shuffle(data)

    X = data_shuffled[['Density_burst', 'Density_throttling']]
    y = data_shuffled['Quality']

    data_norm = data_shuffled.copy()

    for column in ['Density_burst', 'Density_throttling']:
        data_norm[column] = ((data_norm[column] - data_norm[column].min()) /
                                (data_norm[column].max() - data_norm[column].min()))
        

    # KNN

    X = data_norm[['Density_burst', 'Density_throttling']]
    y = data_norm['Quality']

    best_score = 0.0
    i_best_score = 0
    for i in range(1, 30):
        model = KNeighborsClassifier(n_neighbors = i)
        scores = cross_val_score(model, X, y, cv=10, scoring = 'accuracy')
        n_spaces = 1 - i // 10
        if (scores.mean() > best_score):
            best_score = scores.mean()
            i_best_score = i

    print("KNN best result:")
    print("n =", i_best_score)
    print("accuracy = %.2f" % best_score)
    print()

    result_string += f"KNN best result: \nn = {i_best_score}\naccuracy = {str(best_score)[:5]}\n\n"

    KNN_best = best_score

    # SVC

    best_score = 0.0
    best_kernel = ''
    for i_kernel in (['linear', 'poly', 'rbf', 'sigmoid']):
        X_norm = data_norm[['Density_burst', 'Density_throttling']]
        y_norm = data_norm['Quality']
        clf = make_pipeline(StandardScaler(), SVC(gamma='auto', kernel=i_kernel))
        scores = cross_val_score(clf, X_norm, y_norm, cv=10, scoring = 'accuracy')
        n_spaces = 8 - len(i_kernel)
        if (scores.mean() > best_score):
            best_score = scores.mean()
            best_kernel = i_kernel
        
    print("SVC best result:")
    print("kernel =", best_kernel)
    print("accuracy = %.2f" % best_score)
    print()

    result_string += f"SVC best result: \nkernel = {best_kernel}\naccuracy = {str(best_score)[:5]}\n\n"

    SVC_best = best_score

    # CatBoost

    best_score = 0.0
    best_params = []
    # for iter_param in ([100, 200, 500, 1000, 2000]):
        # for cv_param in ([5, 10, 20]):
            # for lr_param in ([0.05, 0.2, 0.5, 0.7, 1]):
    for iter_param in ([200]):
        for cv_param in ([10]):
            for lr_param in ([0.05]):
                model = CatBoostClassifier(iterations=iter_param, learning_rate = lr_param, silent=True)
                scores = cross_val_score(model, X, y, cv=cv_param, scoring = 'accuracy')
                n_spaces_i = 1 - iter_param // 1000
                n_spaces_j = 1 - cv_param // 10
                n_spaces_k = 5 - len(str(lr_param))
                if (scores.mean() > best_score):
                    best_score = scores.mean()
                    best_params = [iter_param, cv_param, lr_param]

    print("CatBoost best result:")
    print(f"iterations = {best_params[0]}, cv = {best_params[1]}, learning_rate = {best_params[2]}")
    print("accuracy = %.2f" % best_score)
    print()

    result_string += "CatBoost best result: \n"
    result_string += f"iterations = {best_params[0]}, cv = {best_params[1]}"
    result_string += f"learning_rate = {best_params[2]}\naccuracy = {str(best_score)[:5]}\n\n"

    CatBoost_best = best_score

    if KNN_best >= SVC_best and KNN_best >= CatBoost_best:
        print("Best classifier is KNN with accuracy = %.2f" % KNN_best)
        result_string += f"Best classifier is KNN with accuracy = {str(KNN_best)[:5]}"
    elif SVC_best >= KNN_best and SVC_best >= CatBoost_best:
        print("Best classifier is SVC with accuracy = %.2f" % SVC_best)
        result_string += f"Best classifier is SVC with accuracy = {str(SVC_best)[:5]}"
    else:
        print("Best classifier is CatBoost with accuracy = %.2f" % CatBoost_best)
        result_string += f"Best classifier is CatBoost with accuracy = {str(CatBoost_best)[:5]}"

    with open("result.txt", "w") as text_file:
        text_file.write(result_string)

    print("\nResult is saved in result.txt")
    