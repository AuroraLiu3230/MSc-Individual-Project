import os, glob
import pandas as pd

path = "/Users/liuhsiaoching/Desktop/Dissertation/Data/Month"

all_files = glob.glob(os.path.join(path, "EURGBP_2021*.csv"))
all_files.sort()


df = (pd.read_csv(f, sep=",", header=None) for f in all_files)
df_merged = pd.concat(df, ignore_index=True)
df_merged.to_csv("/Users/liuhsiaoching/Desktop/Dissertation/Data/Year/EURGBP_2021.csv", header=False, index=False)

for i in range(4):
    df = (pd.read_csv(f, sep=",", header=None) for f in all_files[3*i:3*(i+1)])
    df_merged = pd.concat(df, ignore_index=True)
    df_merged.to_csv("/Users/liuhsiaoching/Desktop/Dissertation/Data/Quarter/EURGBP_2021Q%s.csv"%(i+1), header=False, index=False)

