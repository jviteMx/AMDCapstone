# MIT LINCENCE. 2021
#
# This file is part of an academic capstone project,
# and it is made for AMD as part of efforts to automate
# the open source ROCM math libraries performance analytics.
# Contact The AMD rocm team for use and improvements on the project.
# The team: Victor Tuah Kumi, Aidan Forester, Javier Vite, Ahmed Iqbal
# Reach Victor Tuah Kumi or Ahmed Iqbal on LinkedIn

"""Processes the data files inside the MongoDB Database and returns computed statistics - such as linear regression
 - between two columns of the users choice. This analyzer is separate from the dashboard, as it will be used to get
 an understanding of the data before viewing in the dashboard. For the scope of this project, a calculation of the
 Linear Regression equation and R-Squared value will be computed."""


from mongo_read import MongoReader
from sklearn.linear_model import LinearRegression

reader = MongoReader()


def regression(df, col1, col2):
    """Computes the R-Squared value and Linear Regression equation for two selected columns based on user input"""
    model = LinearRegression()
    x = df[col1].to_numpy().reshape(-1, 1)
    y = df[col2].to_numpy().reshape(-1, 1)
    model.fit(x, y)
    r_sq = model.score(x, y)  # coefficient of determination (R^2)
    b = model.intercept_  # y intercept
    m = model.coef_  # slope
    return r_sq, b, m


# return the df from a search
def search(reader, database, collection):
    """Searches for the data in the database, and returns it as a dataframe"""
    df = MongoReader.read_collection(reader, database=database, collection=collection)
    return df


if __name__ == '__main__':
    database = input("Please input the database name: ")
    collection = input('Please input the collection name: ')
    # df = search(reader, database='gpu_server_1', collection = 'gpu_server_1/rocfft/rocm3.6/r2-d1-c2c-op')
    df = search(reader, database = database, collection = collection)

    x = input("Please input the first column for regression computation (ie: x-axis): ")
    y = input("Please input the second column for regression computation (ie: y-axis): ")

    r_sq, b, m = regression(df=df, col1=x, col2=y)
    # r_sq, b, m = regression(df=df, col1='xlength', col2='mean')
    print("R-Squared value: ", r_sq)
    print("Equation: y = ", m, "x + ", b)
