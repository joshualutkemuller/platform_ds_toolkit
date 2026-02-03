def validate_schema(df, cols): missing=set(cols)-set(df.columns); missing and (_ for _ in ()).throw(ValueError(missing))
