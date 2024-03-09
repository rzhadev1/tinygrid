from matpowercaseframes import CaseFrames

# load case files
case_path = 'Texas7k_20210804.m'
case_frame = CaseFrames(case_path)
print(case_frame.to_csv('./config'))
print(case_frame.to_excel('./config/texas_case.xlsx'))
