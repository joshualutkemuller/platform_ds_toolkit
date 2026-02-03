def assert_no_nulls(df, cols):
  [(_ for _ in ()).throw(ValueError(c)) for c in cols if df[c].isna().any()]
