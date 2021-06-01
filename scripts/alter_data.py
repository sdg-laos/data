def alter_data(df, context):
    if 'REF_AREA' in df:
        df = df.assign(GeoCode=df['REF_AREA'])
    return df
