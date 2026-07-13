
import numpy as np
import pandas as pd
from scipy.stats import Binomial
from statsmodels.stats.contingency_tables import mcnemar

df = pd.DataFrame(pd.read_csv("/Users/Anton_Sadeghi/Desktop/data_sorted.csv"))

PATIENTS = 55

cutoff_3 = 80.0 # t1rho (kanske)
cutoff_4 = 64.0 # t2 (kanske)

zeros = 0
ones = 0
twos = 0
threes = 0

for i in range(PATIENTS):
    patient_df = df[df['patient'] == i].copy()
    for j in range(5):
        slice_df = patient_df[patient_df['slice'] == j].copy()
        try:
            method_3 = slice_df[slice_df['method'] == 3].copy()
            #print(method_3)
            
            val_3 = method_3.iloc[0].to_numpy()[4]
            

            
            method_4 = slice_df[slice_df['method'] == 4].copy()
            val_4 = method_4.iloc[0].to_numpy()[4]
            
            assert method_3.shape[0] == 1
            assert method_4.shape[0] == 1
            assert (not np.isnan(val_3) ) and (not np.isnan(val_4))
            #print(val_3, val_4)
            #print("success")

            if val_3 < cutoff_3 and val_4 < cutoff_4:
                zeros += 1
            elif val_3 >= cutoff_3 and val_4 >= cutoff_4:
                ones += 1
            elif val_3 < cutoff_3 and val_4 >= cutoff_4:
                twos += 1
            else:
                threes += 1
        except:
            pass
            #print("fail")

# print(zeros)
# print(ones)
# print(twos)
# print(threes)

# data = [[ones, twos], [threes, zeros]]
# print(mcnemar(data, exact=True))
# P = (ones+twos/2+threes/2)/(zeros + ones + twos + threes)
# print(P)
b = Binomial(n=twos+threes, p=0.5)
print("T2:")
print("p =", 1 - b.cdf(threes - 1))

