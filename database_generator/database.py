import pandas as pd
import numpy as np


class Database:
    def __merge_column(self,dataframe, column_name):
        df = dataframe.copy()
        df_view = df[column_name]
        merge_columns = list()
        for _,row in df_view.iterrows():
            non_nan_elements = [el for el in row if el == el]
            if len(non_nan_elements):
                merge_columns.append(non_nan_elements[0])
            else:
                merge_columns.append(np.nan)
        del df[column_name]
        df[column_name] = merge_columns
        return df


    def __merge_all_columns(self,dataframe):
        df = dataframe.copy()
        duplicate_columns = list(set([col for col in df.columns if list(df.columns).count(col)>1]))
        for col in duplicate_columns:
            df = self.__merge_column(df,col)
        return df

    def __string_to_float(self,string):
        if "kcal" in string:
            cut_string = string.split("kcal")[0]
            if "(" in cut_string:
                return float(cut_string.split("(")[1])
            else:
                return float(cut_string)
        elif 'g' in string:
            cut_string = string.split(" ")
            if len(cut_string) == 2:
                return float(cut_string[0])
            else:
                try:
                    return float(cut_string[1])
                except:
                    return float(cut_string[0])
        else:
            if "kJ" in string:
                return float(string.split("kJ")[0])*0.239
            else:
                return float(string)

            
    def __construct_database(self):
        database = pd.read_excel("./data/ah_product_database.xlsx")
        database.columns = [col_name.rstrip().lstrip() for col_name in database.columns]
        database = self.__merge_all_columns(database)

        critical_values_database = database[["Eiwitten","Energie","Vet","Koolhydraten"]]
        critical_values_database = critical_values_database.dropna(axis="index",how="any")

        database = database.loc[critical_values_database.index].set_index("name")
        
        database["Carbs(g)"] = database["Koolhydraten"].map(self.__string_to_float)

        database["Fats(g)"] = database["Vet"].map(self.__string_to_float)        
        database["Kcals"] = database["Energie"].map(self.__string_to_float)
        database["Grams"] = [100 if "100 gram" in str(el).lower() else np.nan for el in database["Soort Per"]]
        database["mL"] = [100 if "100 milliliter" in str(el).lower() else np.nan for el in database["Soort Per"]]

        return database

    def __new__(cls, *args, **kwargs):
        # This is python magic to allow you to just instantiate the class
        # and use it as a normal dataframe
        instance = super(Database, cls).__new__(cls, *args, **kwargs)
        return instance.__construct_database()
