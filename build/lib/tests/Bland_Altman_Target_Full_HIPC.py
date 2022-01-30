# Copyright (C) 2021, Paul Freulon <paul.freulon@math.u-bordeaux.fr>=
#
# License: MIT (see COPYING file)

import numpy as np
import pandas as pd

from CytOpT import Bland_Altman


class Bland_Altman_Full_HIPC:

    def __init__(self, data):
        """
        2D projection using two markers.
        The data are divided into two classes: the CD4 cells where the CD4 marker is present and the CD8 cells where the CD8 marker is present.
        """
        self.data = data

    def get_length_unique_numbers(self, values):
        list_of_unique_value = []

        unique_values = set(values)

        for number in unique_values:
            list_of_unique_value.append(number)

        return {'list_of_unique_value': list_of_unique_value, 'length': len(list_of_unique_value)}

    def plotBlandAltman(self):
        self.data['True_Prop'] = self.data['True_Prop'].drop(['Baylor1A'])
        self.data['Estimate_Prop'] = self.data['Estimate_Prop'] .drop(['Baylor1A'])
        self.data['Estimate_Prop'] = np.asarray(self.data['Estimate_Prop'])
        self.data['True_Prop'] = np.asarray(self.data['True_Prop'])
        Diff_prop = self.data['True_Prop'].ravel() - self.data['Estimate_Prop'].ravel()
        Mean_prop = (self.data['True_Prop'].ravel() + self.data['Estimate_Prop'].ravel()) / 2

        Classes = np.tile(np.arange(1, 11), 61)
        Centre_1 = np.repeat(['Yale', 'UCLA', 'NHLBI', 'CIMR', 'Miami'], 10)
        Centre_2 = np.repeat(['Standford', 'Yale', 'UCLA', 'NHLBI', 'CIMR', 'Baylor', 'Miami'], 10)
        Centre = np.hstack((Centre_1, Centre_2, Centre_2, Centre_2,
                            Centre_2, Centre_2, Centre_2, Centre_2, Centre_2))

        Patient1A = np.repeat(1, 50)
        Patient2 = np.repeat(2, 70)
        Patient3 = np.repeat(3, 70)
        Patient1 = np.repeat(1, 70)

        Patient = np.hstack((Patient1A, Patient2, Patient3,
                             Patient1, Patient2, Patient3,
                             Patient1, Patient2, Patient3))

        Dico_res = {'h_true': self.data['True_Prop'].ravel(), 'h_hat': self.data['Estimate_Prop'].ravel(),
                    'Diff': Diff_prop, 'Mean': Mean_prop, 'Classe': Classes,
                    'Center': Centre, 'Patient': Patient}
        df_res_Cytopt = pd.DataFrame(Dico_res)
        df_res_Cytopt['Classe'] = df_res_Cytopt['Classe'].astype('object')
        return df_res_Cytopt


if __name__ == '__main__':
    import seaborn as sns
    data = {'Estimate_Prop': pd.read_csv('data/Res_Estimation_Stan1A.txt', index_col=0),
            'True_Prop': pd.read_csv('data/True_proportion_Stan1A.txt', index_col=0)}

    test2 = Bland_Altman_Full_HIPC(data)
    prop = test2.plotBlandAltman()
    proportions = prop[["h_true", "h_hat"]]
    proportions.columns = ["Gold_standard", "desasc"]
    Bland_Altman(proportions, list(prop["Classe"]))
