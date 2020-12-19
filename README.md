# Django web app patents classification

This app web scrapes Live a patent and predicts how many of its claims are either product or process claims. The result is the percentage of the claims in patent that are product claims. A percentage of product claims of 50% means that a half of the claims in a patent are product claims and the other half are process claims. 
To predict the percentage of product claims, after web scraping the patents, its text is coverted into a numeric feature vector with TF-IDF vectorization and a Gradient Boosting Classifiers - XGBOOST - is applied to predict the claims either as product or process claims (click on About ML model if you want to know more info on how the model was trained).

The machine learning model was trained with around 400 patents with a total of around 7000 claims manually labelled from both EPO and USPTO offices. To train, validate and test the model, the data was split respectively, 50% for training, 25% for validating and 25% for testing. Only on the training data, to compesate of the imbalance classes, an oversampling method was applied. Both the TF-IDF vectorizer and the XGBOOST algorithm have been tuned using the validation data.

