state_attributes = [
    ('AL', 'Alabama', 'html_attribute_AL'),
    ('AK', 'Alaska', 'html_attribute_AK'),
    ('AZ', 'Arizona', 'html_attribute_AZ'),
    ('AR', 'Arkansas', 'html_attribute_AR'),
    ('CA', 'California', 'html_attribute_CA'),
    ('CO', 'Colorado', 'html_attribute_CO'),
    ('CT', 'Connecticut', 'html_attribute_CT'),
    ('DE', 'Delaware', 'html_attribute_DE'),
    ('FL', 'Florida', 'html_attribute_FL'),
    ('GA', 'Georgia', 'html_attribute_GA'),
    ('HI', 'Hawaii', 'html_attribute_HI'),
    ('ID', 'Idaho', 'html_attribute_ID'),
    ('IL', 'Illinois', 'html_attribute_IL'),
    ('IN', 'Indiana', 'html_attribute_IN'),
    ('IA', 'Iowa', 'html_attribute_IA'),
    ('KS', 'Kansas', 'html_attribute_KS'),
    ('KY', 'Kentucky', 'html_attribute_KY'),
    ('LA', 'Louisiana', 'html_attribute_LA'),
    ('ME', 'Maine', 'html_attribute_ME'),
    ('MD', 'Maryland', 'html_attribute_MD'),
    ('MA', 'Massachusetts', 'html_attribute_MA'),
    ('MI', 'Michigan', 'html_attribute_MI'),
    ('MN', 'Minnesota', 'html_attribute_MN'),
    ('MS', 'Mississippi', 'html_attribute_MS'),
    ('MO', 'Missouri', 'html_attribute_MO'),
    ('MT', 'Montana', 'html_attribute_MT'),
    ('NE', 'Nebraska', 'html_attribute_NE'),
    ('NV', 'Nevada', 'html_attribute_NV'),
    ('NH', 'New Hampshire', 'html_attribute_NH'),
    ('NJ', 'New Jersey', 'html_attribute_NJ'),
    ('NM', 'New Mexico', 'html_attribute_NM'),
    ('NY', 'New York', 'html_attribute_NY'),
    ('NC', 'North Carolina', 'html_attribute_NC'),
    ('ND', 'North Dakota', 'html_attribute_ND'),
    ('OH', 'Ohio', 'html_attribute_OH'),
    ('OK', 'Oklahoma', 'html_attribute_OK'),
    ('OR', 'Oregon', 'html_attribute_OR'),
    ('PA', 'Pennsylvania', 'html_attribute_PA'),
    ('RI', 'Rhode Island', 'html_attribute_RI'),
    ('SC', 'South Carolina', 'html_attribute_SC'),
    ('SD', 'South Dakota', 'html_attribute_SD'),
    ('TN', 'Tennessee', 'html_attribute_TN'),
    ('TX', 'Texas', 'html_attribute_TX'),
    ('UT', 'Utah', 'html_attribute_UT'),
    ('VT', 'Vermont', 'html_attribute_VT'),
    ('VA', 'Virginia', 'html_attribute_VA'),
    ('WA', 'Washington', 'html_attribute_WA'),
    ('WV', 'West Virginia', 'html_attribute_WV'),
    ('WI', 'Wisconsin', 'html_attribute_WI'),
    ('WY', 'Wyoming', 'html_attribute_WY')
]


descriptions = {}
for state_abbr, state_name, html_attribute in state_attributes:
    print("case '{}':".format(state_abbr))
    print("description = '<b>{}: '''+str({})+''';".format(state_name, html_attribute))
    print("break;")



print(descriptions)


