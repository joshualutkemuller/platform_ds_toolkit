import pandas as pd

def to_long(df, id_vars, value_vars): return df.melt(id_vars=id_vars, value_vars=value_vars)
